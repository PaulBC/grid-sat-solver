import re
from .clausebuilder import Literal, ZERO

IMPLIED_BY = '<-'

def parse_tokens(line):
  '''Parse a line of text with symbols.'''
  line = line.strip()
  if not line or line.startswith('#'):
    line = line[1:]
    return line[1:] if line.startswith(' ') else line, False
  return line.split(), True

def parse_line(line):
  '''Parse a line of text with symbols.'''
  tokens, split = parse_tokens(line)
  if not split:
    return tokens
  # if needed, convert 'B <- A0 ... An' to 'B ~AO ... ~An'
  if len(tokens) >= 2 and tokens[1] == IMPLIED_BY:
    return tuple([Literal.parse(tokens[0])] + [~Literal.parse(token) for token in tokens[2:]])

  return tuple(Literal.parse(token) for token in tokens)

def parse_lines(lines):
  return [parse_line(line) for line in lines.strip().split('\n')]

def is_comment(clause):
  '''Check if a symbolic clause is a string comment.'''
  return isinstance(clause, str)

def clause_to_string(clause, consequent):
  '''Convert clause to a string, in implication form if consequent is present.'''
  head = list(filter(lambda x: x.name == consequent, clause))
  if head:
     clause = head + [IMPLIED_BY] + [~x for x in clause if x.name != consequent]
  return ' '.join(map(str, clause))

def find_variables(symbolic_clauses):
  '''Finds variables in symbolic clauses.'''
  variables = set()
  for clause in symbolic_clauses:
    if not is_comment(clause):
      for literal in clause:
        variables.add(literal.name)
  return variables

def inflate_template(template_constraints, substitution_maps, consequent=None,
                     adjust_tag=lambda orientation, tag: tag):
  '''Inflates each template clause using substitutions.'''
  # create symbolic clauses for mapped variables using template
  clauses = []
  has_zero = False
  substituted = set.union(*[set(submap.keys())
                          for submap in substitution_maps if not is_comment(submap)])
  for constraint in template_constraints:
    if is_comment(constraint) or not substituted.intersection([lit.name for lit in constraint]):
      clauses.append(constraint)
    else:
      clauses.append('Template: ' + clause_to_string(constraint, consequent))
      # apply the constraint to each grid cell
      for substitution in substitution_maps:
        if is_comment(substitution):
          clauses.append(substitution)
        else:
          clause = []
          for literal in constraint:
            info = substitution.get(literal.name)
            if info:
              literal = Literal(info[0], literal.value, adjust_tag(info[1], literal.tag))
            clause.append(literal)
            if literal.name == ZERO.name:
              has_zero = True
          if not (ZERO in clause and ~ZERO in clause):
            clauses.append(clause)
  if has_zero:
    clauses.append([~ZERO])
  return clauses

def to_substitution_tuples(substitution_maps, key_order=[]):
  '''Makes a list of string tuples from a set of substitution maps.'''
  def to_string(pair):
   tok = pair[0]
   if pair[1] != 0:
     tok += ',%s' % pair[1]
   return tok

  allkeys = set()
  for mapping in substitution_maps:
    if not is_comment(mapping):
      allkeys.add(tuple(sorted(mapping.keys())))
  assert len(allkeys) == 1
  keys = list(next(iter(allkeys)))

  # use given key order with default to original ordering.
  keys = [key for key in key_order if key in keys] + [key for key in keys if key not in key_order]

  tuples = []
  for mapping in substitution_maps:
    if is_comment(mapping):
      tuples.append(mapping)
    else:
      tuples.append(tuple(to_string(mapping[key]) for key in keys))

  return [keys] + sorted(tuples)

def to_substitution_map(substitution_tuples):
  '''Makes a list of maps from a set of substitution tuples.'''
  def from_string(tok):
    fields = tok.split(',')
    return (fields[0], 0 if len(fields) == 1 else int(fields[1]))

  maps = []
  # first find the row with key names for template
  pos = 0
  while is_comment(substitution_tuples[pos]):
    maps.append(substitution_tuples[pos])
    pos += 1
  keys = substitution_tuples[pos]

  # now construct maps for remaining non-comment tuples
  for values in substitution_tuples[pos + 1:]:
    if is_comment(values):
      maps.append(values)
    else:
      maps.append(dict(zip(keys, [from_string(value) for value in values])))
  return maps
