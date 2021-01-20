import random
import sys

from symsat.gridbuilder import *
from symsat.tesselation import *
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

  # add clauses for a cardinality bound of >= 50 in first generation
  clauses.extend(bound_population(grid, GreaterThanOrEqual, 50))

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

  draw_hex_cells(xorig, yorig, cells)

  print()
  print('Hex tile patch with symmetry %s' % equivalence)
  width = len(cells[0])
  for i in range(len(cells)):
    print((' ' * (width - i)) + ' '.join(['O' if x else '.' for x in cells[i]]))

if __name__ == "__main__":
  run_hextile(sys.argv[1], HEX_CONSTRAINTS, Tesselated(RotatedRhombus(16)), -250, 250)
  input('Press enter to exit.')
