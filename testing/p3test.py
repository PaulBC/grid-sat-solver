import random
import sys

from symsat.gridbuilder import *
from symsat.tesselation import *
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
  # stator is true iff two consecutive live generations
  stator$ <- G O
  ~stator$ <- ~G
  ~stator$ <- ~O
'''))

def run_p2patch(fileroot, life_constraints, equivalence, num_stators=0):
  dimacs_file = fileroot + '.dim'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence, PeriodicTimeAdjust(3, 0, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  clauses = inflate_grid_template(life_constraints, grid, G.name)

  # add clauses for a cardinality bound of >= 15 in first generation
#  clauses.extend(bound_population(grid, GreaterThanOrEqual, 8, 0))

  # add clauses for exact number of stators.
  clauses.extend(bound_helper(grid, LessThanOrEqual, num_stators, 'stator', 0))
#  clauses.extend(bound_helper(grid, GreaterThanOrEqual, num_stators, 'stator', 0))

  oncell = root.go(SE, SE, SE)
  clauses.append((oncell,))
  clauses.append((~oncell.go(G),))

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
  print('Period-%d patch with symmetry %s' % (root.timeadjust.period, root.equivalence))
  for i in range(len(cells)):
    print(''.join(['*' if x else '.' for x in cells[i]]))

if __name__ == "__main__":
  if len(sys.argv) > 2:
    set_solver(sys.argv[2]) 
  run_p2patch(sys.argv[1], LIFE_CONSTRAINTS, Tesselated(RotatedSquare(9)), 4)
