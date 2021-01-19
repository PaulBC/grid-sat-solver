import sys

from gridbuilder import *
from tesselation import *
from clausebuilder import *
from rulesymmetry import *
from dimacs_sat import *
from solver import *

dimacs_file = sys.argv[1] + '.dim'
symbolic_file = sys.argv[1] + '.sym'
solution_file = sys.argv[1] + '.out'

all_constraints = expand_symmetry(TOTALISTIC, parse_lines('''
  # death by loneliness or crowding
  ~G <- ~N ~NE ~E ~SE ~S ~SW ~W
  ~G <- N NE E SE
  # birth on 3 neighbors
   G <- N NE E ~SE ~S ~SW ~W ~NW
  # survival on 2 or 3 neighbors
  ~G <- ~O N NE ~E ~SE ~S ~SW ~W ~NW
   G <- O N NE ~E ~SE ~S ~SW ~W ~NW
'''))

# make CA grid
#root = MooreGridNode((0, 0, 0), Toroidal(10, 10, 3), PeriodicTimeAdjust(1, 0, 0))
root = MooreGridNode((0, 0, 0), Tesselated(RotatedSquare(10)), PeriodicTimeAdjust(1, 0, 0))
#root = MooreGridNode((0, 0, 0), Tesselated(CrossSurface(10, 10)), PeriodicTimeAdjust(1, 0, 0))
grid = build_grid(root)

# create clauses for life rule conditions on grid
clauses = inflate_grid_template(all_constraints, grid, G.name)

# add clauses for a cardinality bound of >= 30 in first generation
clauses.extend(bound_population(grid, GreaterThanOrEqual, 30))

# optionally set boundary to 0
'''
for i in range(2):
  for j in range(root.equivalence.columnsize):
    clauses.append((~Literal('c_%d_%d_0' % (i, j)),))
'''

# write dimacs file for solver
with open(dimacs_file, 'w') as out:
  output_dimacs(clauses, out)

# write symbolic form of clauses
with open(symbolic_file, 'w') as out:
  output_symbolic(clauses, out)

# solve and print results
results = solve(dimacs_file, solution_file)
valuegrid = get_value_grid('c', results)

cells = []
for i in range(len(valuegrid[0]) * 2):
  row = []
  for j in range(len(valuegrid[0][0]) * 2):
    it, jt, _ = root.equivalence.to_equivalent(i, j)
    row.append(valuegrid[0][it][jt])
  cells.append(row)

for i in range(len(cells)):
  print("".join(['*' if x else '.' for x in cells[i]]))
