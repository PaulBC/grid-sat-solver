import random
import sys

from symsat.clausebuilder import *
from symsat.dimacs_sat import *
from symsat.solver import solve
from symsat.rulesymmetry import expand_symmetry, O, W, S, ROTATED_180_HEX
from symsat.gridbuilder import *
from symsat.solver import *
from symsat.tags import *
from symsat.displayhex import *

def canonical(i, j, k):
  '''Returns a unique representation of triple (i, j, k) up to rotation.'''
  return min((i, j, k), (j, k, i), (k, i, j))

def tri_literal(i, j, k):
  '''Returns a literal based on canonical form of triple (i, j, k).'''
  return Literal('tri_%d_%d_%d' % canonical(i, j, k))

def bound_count(literals, comparator, size):
  '''Assign a cardinality constraint.'''
  cardinality = comparator(literals, size)
  clauses = ['Bounded %s %s' % (comparator.__name__, size)]
  clauses.extend(cardinality.adder_clauses)
  clauses.extend(cardinality.constraint_clauses)
  return clauses

def wait_for_enter(msg='===== Press [ENTER] or [RETURN] to continue ====='):
  '''Wait for user to hit enter before proceeding.'''
  # Use input() but catch exception to be compatible with Python 2 and 3.
  try:
    input(msg)
  except:
    pass

fileroot = 'data/%s' % sys.argv[1]
if len(sys.argv) > 2:
  set_solver(sys.argv[2])
randassign = 0
if len(sys.argv) > 3:
  randassign = int(sys.argv[3])
rulesize = 8
if len(sys.argv) > 4:
  rulesize = int(sys.argv[4])

dimacs_file = fileroot + '.dim'
tag_file = fileroot + '.tag'
symbolic_file = fileroot + '.sym'
solution_file = fileroot + '.out'

all_clauses = []
n = 5
for i in range(n):
  for j in range(n):
    for k in range(n):
      literal = tri_literal(i, j, k)
      all_clauses.append((literal, ~O(i), ~W(j), ~S(k)))
all_clauses = expand_symmetry(ROTATED_180_HEX, all_clauses)
all_clauses.sort()

# make CA grid
root = MooreGridNode((0, 0, 0), Open(20, 20), PeriodicTimeAdjust(1, 0, 0))
grid = build_grid(root)

# create clauses for life rule conditions on grid
tag_clauses = inflate_grid_template(all_clauses, grid, outside_value=None)

# expand clauses to booleans
clauses = expand_tag_clauses(tag_clauses)

# constraints on the rules we will allow
used = set()
for i in range(n):
  for j in range(n):
    if i != j:
      literals = tuple(tri_literal(i, j, k) for k in range(n) if k != i and k != j)
      clauses.append(literals)
      used.update(literals)

excluded  = set()
for i in range(n):
  for j in range(n):
    for k in range(n):
      if i == j or i == k or j == k:
        excluded.add(tri_literal(i, j, k))
for literal in sorted(excluded):
  clauses.append((~literal,))

clauses.append((tri_literal(0, 1, 2),))
clauses.append((~tri_literal(0, 2, 1),))

clauses.extend(bound_count(sorted(used), LessThanOrEqual, rulesize))

base_clauses = clauses

while True:
  clauses = list(base_clauses)

  rand_tag_clauses = []
  # assign some random cells to generate a variety of output
  for rep in range(randassign):
    rand_tag_clauses.append((Literal('c_%d_%d_0' %
                                (random.randint(0, root.equivalence.rowsize - 1),
                                 random.randint(0, root.equivalence.rowsize - 1)), True, 1),))
  clauses.extend(expand_tag_clauses(rand_tag_clauses))

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)

  # write tag form of clauses
  with open(tag_file, 'w') as out:
    output_symbolic(tag_clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file, random.randint(1, 1 << 32), True)
  valuegrid = get_value_grid('c', results)
  print(' '.join([name for name, value in results if value and name.startswith('tri')]))

  cells = []
  for i in range(2 * len(valuegrid[0])):
    row = []
    for j in range(2 * len(valuegrid[0][0])):
      it, jt, _ = root.equivalence.to_equivalent(i, j)
      try:
        row.append(valuegrid[0][it][jt])
      except:
        pass
    cells.append(row)

  COLORS =  COLORS = ['#4f1111', '#ffffff', '#ffff4f', '#114f11', '#11114f']
  draw_hex_cells(-200, 300, cells, 20, COLORS)

  print()
  print('Hex tile patch with symmetry %s' % root.equivalence)
  width = len(valuegrid[0])
  for i in range(width):
    print((' ' * (width - i)) + ' '.join([str(cells[i][j]) for j in range(len(valuegrid[0][0]))]))

  wait_for_enter()
