from collections import defaultdict
from functools import reduce

from .clausebuilder import Literal, collect_literals, expand_disjunction

def match_integers_all(literals, max_tags):
  '''Make a conjunction asserting equality and inequality between bit vectors and integers.'''
  conjunction = []
  for literal in literals:
    if literal.is_bool():
      conjunction.append((literal,))
    else:
      maxv = max_tags[literal.name]
      assert literal.tag <= maxv
      bitmatchers = bit_literals(literal, maxv)
      if literal.value:
        conjunction.extend((x,) for x in bitmatchers)
      else:
        conjunction.append(tuple(bitmatchers))
  return conjunction

def bit_variable(name, bit):
  '''Create a variable name for a bit in a numeric variable.'''
  return "%s#%d" % (name, bit)

def bit_literals(literal, maxv):
  '''Make literals representing the bits of a single integer match.'''
  return [Literal(bit_variable(literal.name, i), not (literal.tag >> i & 1 == 1) ^ literal.value)
          for i in range(maxv.bit_length())]

def match_integers_any(literals, max_tags):
  '''Make clauses for a disjunction asserting at least one integer equality or inequality holds.'''
  disjunction = [match_integers_all([literal], max_tags) for literal in literals]
  return sorted(reduce(expand_disjunction, disjunction))

def find_max(value_lists):
  '''Find the maximum tag of each numeric variable.'''
  max_tags = {}
  for literal in collect_literals(value_lists):
    if not literal.is_bool():
      max_tags[literal.name] = max(literal.tag, max_tags.get(literal.name, 0))
  return max_tags

def make_or_of_ands_matcher(integer_matches, max_tags=None):
  '''Make a list of conjunctions for each tuple of integer literals.
     Max tags are computed or can be supplied.'''
  if max_tags is None:
    max_tags = find_max(integer_matches)
  return [match_integers_all(literals, max_tags) for literals in integer_matches]


def constant_max(tag):
  '''Return a dictionary with a constant max tag value.'''
  return defaultdict(lambda: tag)

def make_matching_clauses(literal_tuples):
  '''Makes a set of tag clauses that matches one of the given tuples of literals.'''
  maxtags = find_max(literal_tuples)
  names = sorted(maxtags.keys())
  # validate that they all use the same literals
  for matcher in literal_tuples:
    if sorted([x.name for x in matcher]) != names:
      raise Exception('%s does not match names: %s' % (matcher, names))
    if any(x.is_bool() for x in matcher):
      raise Exception('%s is not a tag tuple.' % (matcher,))
  # collect inverse clause for each matcher
  inverse_clauses = set()
  for matcher in literal_tuples:
    inverse_clauses.add(tuple(sorted(~x for x in matcher)))

  # return cartesian product of inverse clauses minus those for matching tags
  disjunction = [[(Literal(name, False, i),) for i in range(maxtags[name] + 1)] for name in names]
  return sorted(reduce(expand_disjunction, disjunction).difference(inverse_clauses))

def less_than(literal, limit):
  '''Generate clauses to set an upper limit on a tag literal.'''
  if limit <= 0:
    raise ValueError('%d is not a positive integer.' % limit)

  bits = [limit & (1 << i) for i in range((limit).bit_length())]
  clauses = []
  n = len(bits)
  while any(bits):
    clauses.append(tuple(Literal(bit_variable(literal.name, i), False) for i in range(n) if bits[i]))
    for i in range(min(j for j in range(n) if bits[j]), n):
      if bits[i]:
        bits[i] = 0
      else:
        bits[i] = 1
        break
  return clauses

def inverse_adjust(adjust_tag):
  '''Uses a linear search to find the inverse of an adjust_tag function.
     In practice, there should only be a few tags to check.'''

  def inverse(orientation, adjusted):
    tag = 0
    while True:
      if adjust_tag(orientation, tag) == adjusted:
        return tag
      tag += 1

  return inverse

def expand_tag_clauses(clauses):
  '''Expand any clauses with tags into bit clauses using maximum values found.'''
  max_tags = find_max(clauses)
  # if there are no tags, just return original clauses
  if not max_tags:
    return clauses

  # expand tag clauses into bit clauses
  expanded = []
  for tag_clause in clauses:
    if isinstance(tag_clause, str):
      expanded.append(tag_clause)
    else:
      expanded.extend(match_integers_any(tag_clause, max_tags))

  # set upper bound on bit representations
  expanded.append('Setting upper bound on tags.')
  for tag, value in sorted(max_tags.items()):
    expanded.extend(less_than(Literal(tag), value + 1))

  return expanded
