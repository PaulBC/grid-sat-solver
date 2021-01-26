import random
import sys

from symsat.gridbuilder import *
from symsat.tessellation import *
from symsat.clausebuilder import *
from symsat.displayhex import *
from symsat.rulesymmetry import *
from symsat.dimacs_sat import *
from symsat.solver import *

HEX_CONSTRAINTS = expand_symmetry(ROTATED_HEX, parse_lines('''
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

HEX_CONSTRAINTS.extend(expand_symmetry(TOTALISTIC_HEX, parse_lines('''
  # death on >= 3
  ~G <- NW N E
''')))

def run_hextile(fileroot, hex_constraints, equivalence, xorig, yorig):

  dimacs_file = fileroot + '.dim'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence, PeriodicTimeAdjust(1, 0, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  clauses = inflate_grid_template(hex_constraints, grid, G.name)

  # add clauses for a cardinality bounds
  size = equivalence.rowsize * equivalence.rowsize // 2 - 30
  # clauses.extend(bound_population(grid, LessThanOrEqual, size))
  clauses.extend(bound_population(grid, GreaterThanOrEqual, size))

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
  for i in range(2 * len(valuegrid[0])):
    row = []
    for j in range(2 * len(valuegrid[0][0])):
      it, jt, _ = root.equivalence.to_equivalent(i, j)
      diagonal = j - i
      if diagonal <= equivalence.rowsize and diagonal > -equivalence.rowsize:
        row.append(valuegrid[0][it][jt])
      else:
        row.append(None)
    cells.append(row)

  draw_hex_cells(xorig, yorig, cells)

if __name__ == "__main__":
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])
  run_hextile(sys.argv[1], HEX_CONSTRAINTS, Tesselated(RotatedRhombus(16)), -250, 250)
  input('Press enter to exit.')
