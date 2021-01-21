import re
from .clausebuilder import Literal, ZERO
from .symbolic_util import find_variables, parse_line, parse_lines, is_comment
from .tags import expand_tag_clauses

def is_always_true(clause):
  '''Check if clause is always true because it has both a literal and its negation.'''
  positive = set()
  negative = set()
  for literal in clause:
    if literal.value:
      positive.add(literal.name)
    else:
      negative.add(literal.name)
  return len(set(positive).intersection(negative)) > 0

def minimize_clauses(symbolic_clauses):
  '''Remove duplicate clauses, duplicate literals, and clauses that are always true.'''
  seen = set()
  res = []
  for clause in symbolic_clauses:
    if is_comment(clause):
      res.append(clause)
    else:
      deduped = tuple(sorted(set(clause)))
      if deduped not in seen:
        if not is_always_true(deduped):
          seen.add(deduped)
          res.append(deduped)
  return res

def read_symbolic(inp):
  '''Read clauses in symbolic form.'''
  symbolic_clauses = []
  for line in inp:
    symbolic_clauses.append(parse_line(line))
  return symbolic_clauses

def output_symbolic(symbolic_clauses, out):
  '''Output clauses in symbolic form.'''
  for clause in symbolic_clauses:
    if is_comment(clause):
      out.write('#%s%s\n' % ('' if clause.startswith(' ') else ' ', clause))
    else:
      out.write('%s\n' % ' '.join(map(str, clause)))

def output_dimacs(symbolic_clauses, out):
  '''Output clauses in dimacs format.'''
  # first expand tag clauses if any
  symbolic_clauses = expand_tag_clauses(symbolic_clauses)

  variables = find_variables(symbolic_clauses)
  symbol_table = {name: ix for name, ix in zip(sorted(variables), range(1, len(variables) + 1))}
  symbolic_clauses = minimize_clauses(symbolic_clauses)
  num_clauses = sum(not is_comment(clause) for clause in symbolic_clauses)

  out.write('p cnf %d %d\n' % (len(symbol_table), num_clauses))
  for name, ix in sorted(symbol_table.items()):
    out.write('c variable %s: %d\n' % (name.replace('~', ''), ix))
  for clause in symbolic_clauses:
    if is_comment(clause):
      out.write('c %s\n' % clause)
    else:
      num_clause = [(1 if literal.value else -1) * symbol_table[literal.name] for literal in clause]
      out.write('%s 0\n' % ' '.join([str(x) for x in num_clause]))

# regex for parsing comments mapping variable names to numbers
VAR_REGEX = re.compile('^c variable ([^ ]+): ([0-9]+)')

def load_results(input, solution):
  '''Load the results using variable comments in input and solution of SAT solver.'''
  to_symbol = {}
  for line in input:
    m = VAR_REGEX.search(line)
    if m:
      to_symbol[int(m.group(2))] = m.group(1)

  values = {}
  for line in solution:
    toks = line.split()
    if toks[0] == 'v':
      for x in toks[1:]:
        ix = int(x)
        if ix != 0:
          name = to_symbol[abs(ix)]
          parts = name.split('#')
          truth = ix > 0
          if len(parts) == 1:
            values[name] = truth
          else:
            name, bit = parts
            values[name] = values.get(name, 0) | ((1 << int(bit)) if truth else 0)

  return [(key, value) for key, value in sorted(values.items())]

def get_value_grid(name, results):
  '''Return a grid of values for named variable.'''
  cells = []
  imax = 0
  jmax = 0
  genmax = 0
  prefix = name + '_'

  for key, value in results:
    if key.startswith(prefix):
      i, j, gen = map(int, key.split('_')[1:])
      imax = max(imax, i)
      jmax = max(jmax, j)
      genmax = max(genmax, gen)
      cells.append((i, j, gen, value))

  grid = [[[None] * (jmax + 1) for i in range(imax + 1)] for gen in range(genmax + 1)]
  for i, j, gen, value in cells:
    grid[gen][i][j] = value

  return grid
