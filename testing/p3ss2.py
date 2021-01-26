import sys

from symsat.gridbuilder import *
from symsat.tessellation import *
from symsat.clausebuilder import *
from symsat.rulesymmetry import *
from symsat.dimacs_sat import *
from symsat.solver import *

LIFE_CONSTRAINTS = expand_symmetry(TOTALISTIC, parse_lines('''
  # death by loneliness or crowding
  ~G <- ~N ~NE ~E ~SE ~S ~SW ~W
  ~G <- N NE E SE
  # birth on 3 neighbors
   G <- N NE E ~SE ~S ~SW ~W ~NW
  # survival on 2 or 3 neighbors
  ~G <- ~O N NE ~E ~SE ~S ~SW ~W ~NW
   G <- O N NE ~E ~SE ~S ~SW ~W ~NW
'''))

def run_p3ss(fileroot, life_constraints):
  dimacs_file = fileroot + '.dim'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  root = MooreGridNode((0, 0, 0), Open(8, 19), PeriodicTimeAdjust(3, 1, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  clauses = inflate_grid_template(life_constraints, grid, G.name)

  # add clauses for a cardinality bound of == 25 in first generation
  clauses.extend(bound_population(grid, GreaterThanOrEqual, 29))
  #clauses.extend(bound_population(grid, LessThanOrEqual, 26))

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file)
  valuegrid = get_value_grid('c', results)

  print()
  print("Smallest period 3 spaceship in Life:")
  for i in range(len(valuegrid[0])):
    print("".join(['*' if x else '.' for x in valuegrid[0][i]]))

if __name__ == "__main__":
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])
  run_p3ss(sys.argv[1], LIFE_CONSTRAINTS)

