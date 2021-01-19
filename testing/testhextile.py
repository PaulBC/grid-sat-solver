import sys

from gridsat.gridbuilder import *
from gridsat.tesselation import *
from gridsat.clausebuilder import *
from gridsat.displayhex import *
from gridsat.rulesymmetry import *
from gridsat.dimacs_sat import *
from gridsat.solver import *

dimacs_file = sys.argv[1] + '.dim'
symbolic_file = sys.argv[1] + '.sym'
solution_file = sys.argv[1] + '.out'

all_constraints = expand_symmetry(ROTATED_HEX, parse_lines('''
  # birth on 2o
   G <- NW N ~E ~SE ~S ~W
  # survival on 2m
   G <- O NW ~N E ~SE ~S ~W
  ~G <- ~O NW ~N E ~SE ~S ~W
  # death on <=1, 2o, 2p
  ~G <- ~N ~E ~SE ~S ~W
  ~G <- NW N ~E ~SE ~S ~W
  ~G <- NW ~N ~E SE ~S ~W
'''))

all_constraints.extend(expand_symmetry(TOTALISTIC_HEX, parse_lines('''
  # death on >= 3
  ~G <- NW N E
''')))

# make CA grid
root = MooreGridNode((0, 0, 0), Tesselated(RotatedRhombus(15)), PeriodicTimeAdjust(1, 0, 0))
grid = build_grid(root)

# create clauses for life rule conditions on grid
clauses = inflate_grid_template(all_constraints, grid, G.name)

# add clauses for a cardinality bound of >= 34 in first generation
clauses.extend(bound_population(grid, GreaterThanOrEqual, 34))

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
for i in range(len(valuegrid[0]) * 3):
  row = []
  for j in range(len(valuegrid[0][0]) * 3):
    it, jt, _ = root.equivalence.to_equivalent(i, j)
    row.append(valuegrid[0][it][jt])
  cells.append(row)

draw_hex_cells(-200, 200, cells)

width = len(cells[0])
for i in range(len(cells)):
  print(" " * (width - i), " ".join(['O' if x else '.' for x in cells[i]]))
