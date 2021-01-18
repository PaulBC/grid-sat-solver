import re

LITERAL_RE = re.compile(r'(~)?([^\(]+)(\(([0-9]+)\))?')

class Literal(object):
  def __init__(self, name, value = True, tag = None):
    self.name = name
    self.value = value
    self.tag = tag

  @classmethod
  def parse(cls, string_literal):
    m = LITERAL_RE.match(string_literal)
    if not m:
      raise Exception("Cannot parse " + string_literal + " as literal.")
    return Literal(m.group(2), not m.group(1), int(m.group(4)) if m.group(4) else None)

  def __invert__(self):
    return Literal(self.name, not self.value, self.tag)

  def __xor__(self, bool_value):
    return Literal(self.name, self.value^bool_value, self.tag)

  def __call__(self, tag):
    return Literal(self.name, self.value, tag)

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return ('' if self.value else '~') + self.name + ('' if self.tag is None else '(%s)' % self.tag)

  def __eq__(self, other):
    return self.name == other.name and self.value == other.value and self.tag == other.tag

  def __lt__(self, other):
    return ((self.name, self.value, self.tag or 0) < (other.name, other.value, other.tag or 0))

  def __hash__(self):
    return hash((self.name, self.value, self.tag))

  def is_bool(self):
    return self.tag is None

# index for generating temporary variables
VARNUM = 0

# assigns a new temporary variable
def nextvar():
  global VARNUM
  VARNUM += 1
  return Literal('{x%03x}' % VARNUM)

# check if a clause is always true because it has both a literal and its negation
def always_true(clause):
  for literal in clause:
    if ~literal in clause:
      return True
  return False

# combine clauses with OR just by taking a union of terms
def or_clauses(clause1, clause2):
  return set(clause1).union(clause2)

# expand a disjunction of two list of clauses, ignoring clauses that are always true
def expand_disjunction(clauses1, clauses2):
  expanded = set()
  for clause1 in clauses1:
    for clause2 in clauses2:
       combined = or_clauses(clause1, clause2)
       if not always_true(combined):
         expanded.add(tuple(sorted(combined)))
  return expanded

# remove redundant (less restrictive) disjunctions from the list of clauses
def remove_redundant(clauses):
  minimal = []
  for clause in clauses:
    clauseset = set(clause)
    is_subset = False
    for testclause in clauses:
      testclauseset = set(testclause)
      if len(clauseset) > len(testclauseset):
        if testclauseset.issubset(clauseset):
          is_subset = True
          break
    if not is_subset:
      minimal.append(clause)
  return minimal

# flatten a disjunction of clause lists into a single conjunction of clauses
def flatten_disjunction(clause_lists):
  res = clause_lists[0]
  for clause_list in clause_lists:
    res = remove_redundant(expand_disjunction(res, clause_list))
  return res

# get all variable names from any kind of nested expression
def collect_variables(nested):
  return sorted(set(x.name for x in collect_literals(nested)))

# get all literals from any kind of nested expression
def collect_literals(nested):
  return sorted(collect_literals_recur(nested, set()))

def collect_literals_recur(nested, variables):
  if isinstance(nested, Literal):
    variables.add(nested)
  elif not isinstance(nested, str):
    for part in nested:
      collect_literals_recur(part, variables)
  return variables

# find canonical set of clauses by expanding with all variables
def find_canonical(clauses):
  for name in collect_variables(clauses):
    clauses = expand_disjunction(clauses, always_false(name))
  return clauses

# find all true tuples of literals
def find_true_tuples(clauses):
  # find a canonical unsatisfiable list of all clauses for variables
  names = collect_variables(clauses)
  canonical_zero = always_false(names[0])
  for name in names[1:]:
    canonical_zero = expand_disjunction(canonical_zero, always_false(name))

  # true tuples consist of missing canonical clauses with their literals negated
  canonical_clauses = find_canonical(clauses)
  true_tuples = []
  for clause in canonical_zero:
    if clause not in canonical_clauses:
      true_tuples.append(tuple(~x for x in clause))
  return true_tuples

# returns a list of clauses that is always false for some variable
def always_false(name):
  return [(Literal(name, True),), (Literal(name, False),)]

# zero that can be used as a placeholder
ZERO = Literal('{zero}')

class Cardinality(object):
  def build(self, variables, limit):
    network, levels = Cardinality.make_adder_network(variables)
    self.adder_clauses = Cardinality.make_adder_clauses(network, levels)
    self.constraint_clauses = tuple([~levels[i] if (limit & (1<<i)) == 0 else levels[i]]
                                    for i in range(len(levels)))

  # contracts levels of the adder network by applying full adders to triples of bits on
  @staticmethod
  def contract(network, levels):
    nextlevels = {}
    for level, vars in levels.items():
      if len(vars) % 3 == 2:
        vars = list(vars + [ZERO])
      for i in range(0, len(vars) - 2, 3):
        s0 = nextvar()
        s1 = nextvar()
        network.append((s0, s1, vars[i], vars[i + 1], vars[i + 2]))
        nextlevels.setdefault(level, []).append(s0)
        nextlevels.setdefault(level + 1, []).append(s1)
      if len(vars) % 3 != 0:
        nextlevels.setdefault(level, []).extend(vars[len(vars) // 3 * 3:])
    return nextlevels

  # makes a network by contracting the original list of variables with full adders
  @staticmethod
  def make_adder_network(variables):
    levels = {0: variables}
    network = []
    max_bit = len(variables).bit_length() - 1
    while max(len(val) for val in levels.values()) > 1:
      levels = Cardinality.contract(network, levels)
    return network, [levels[i][0] for i in range(len(levels))]

  # makes clauses for the full adders in the network
  @staticmethod
  def make_adder_clauses(network, levels):
    clauses = []
    for (out0, out1, in0, in1, in2) in network:
      clauses.append((out1, ~in0, ~in1))
      clauses.append((out1, ~in0, ~in2))
      clauses.append((out1, ~in1, ~in2))
      clauses.append((out1, out0, ~in0))
      clauses.append((out1, out0, ~in1))
      clauses.append((out1, out0, ~in2))
      clauses.append((out0, ~in0, ~in1, ~in2))

    # return clauses, filtering out any with !~zero and guarantee to be true
    return [clause for clause in clauses if not clause[-1].name == ZERO.name]

class LessThanOrEqual(Cardinality):
  def __init__(self, variables, limit):
    self.build(variables, limit)

class GreaterThanOrEqual(Cardinality):
  def __init__(self, variables, limit):
    self.build([~x for x in variables], len(variables) - limit)

# convert literals to name value/tag pairs
def to_pairs(literals):
  return tuple((literal.name, (literal.value, literal.tag)) for literal in literals)

# convert name value pairs to literals
def from_pairs(pairs):
  return tuple(Literal(name, value, tag) for (name, (value, tag)) in pairs)
