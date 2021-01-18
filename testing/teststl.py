import sys

from gridbuilder import *
from tesselation import *
from clausebuilder import *
from rulesymmetry import *
from dimacs_sat import *
from solver import *

def make_clauses(clause):
  return all_symmetries(parse_line(clause), TOTALISTIC)

dimacs_file = sys.argv[1] + '.dim'
symbolic_file = sys.argv[1] + '.sym'
solution_file = sys.argv[1] + '.out'

print('# generating clauses for CA rule')
lt2 = make_clauses('~G <- ~N ~NE ~E ~SE ~S ~SW ~W')
ge4 = make_clauses('~G <- N NE E SE')
eq3 = make_clauses('G <- N NE E ~SE ~S ~SW ~W ~NW')
eq2a = make_clauses('~G <- ~O N NE ~E ~SE ~S ~SW ~W ~NW')
eq2b = make_clauses('G <- O N NE ~E ~SE ~S ~SW ~W ~NW')
all_constraints = lt2 + ge4 + eq3 + eq2a + eq2b
print('# done')

# make CA grid
#root = MooreGridNode((0, 0, 0), Toroidal(10, 10, 3), PeriodicTimeAdjust(1, 0, 0))
#root = MooreGridNode((0, 0, 0), Tesselated(RotatedSquare(10)), PeriodicTimeAdjust(1, 0, 0))
root = MooreGridNode((0, 0, 0), Tesselated(CrossSurface(10, 10)), PeriodicTimeAdjust(1, 0, 0))
grid = build_grid(root)

# create clauses for life rule conditions on grid
clauses = inflate_grid_template(all_constraints, grid, G.name)

# add clauses for a cardinality bound of >= 12 in first generation
clauses.extend(bound_population(grid, GreaterThanOrEqual, 12))

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
