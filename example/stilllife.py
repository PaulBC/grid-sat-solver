import random
import sys

from gridsat.gridbuilder import *
from gridsat.tesselation import *
from gridsat.clausebuilder import *
from gridsat.rulesymmetry import *
from gridsat.dimacs_sat import *
from gridsat.solver import *

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

def run_stilllife(fileroot, life_constraints, equivalence):
  dimacs_file = fileroot + '.dim'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence, PeriodicTimeAdjust(1, 0, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  clauses = inflate_grid_template(life_constraints, grid, G.name)

  # add clauses for a cardinality bound of >= 30 in first generation
  clauses.extend(bound_population(grid, GreaterThanOrEqual, 30))

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file, random.randint(1, 1 << 32))
  valuegrid = get_value_grid('c', results)

  cells = []
  for i in range(len(valuegrid[0])):
    row = []
    for j in range(len(valuegrid[0][0])):
      it, jt, _ = root.equivalence.to_equivalent(i, j)
      row.append(valuegrid[0][it][jt])
    cells.append(row)

  print()
  print('Still life patch with symmetry %s' % root.equivalence)
  for i in range(len(cells)):
    print(''.join(['*' if x else '.' for x in cells[i]]))

if __name__ == "__main__":
  run_stilllife(sys.argv[1], LIFE_CONSTRAINTS, Tesselated(RotatedSquare(10)))
