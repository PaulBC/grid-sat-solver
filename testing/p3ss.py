import sys

from gridsat.gridbuilder import *
from gridsat.tesselation import *
from gridsat.clausebuilder import *
from gridsat.rulesymmetry import *
from gridsat.dimacs_sat import *
from gridsat.solver import *

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

root = MooreGridNode((0, 0, 0), Open(5, 16), PeriodicTimeAdjust(3, 1, 0))
grid = build_grid(root)

# create clauses for life rule conditions on grid
clauses = inflate_grid_template(all_constraints, grid, G.name)

# add clauses for a cardinality bound of == 25 in first generation
clauses.extend(bound_population(grid, GreaterThanOrEqual, 25))
clauses.extend(bound_population(grid, LessThanOrEqual, 25))

# write dimacs file for solver
with open(dimacs_file, 'w') as out:
  output_dimacs(clauses, out)

# write symbolic form of clauses
with open(symbolic_file, 'w') as out:
  output_symbolic(clauses, out)

# solve and print results
results = solve(dimacs_file, solution_file)
valuegrid = get_value_grid('c', results)

for i in range(len(valuegrid[0])):
  print("".join(['*' if x else '.' for x in valuegrid[0][i]]))
