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

def run_hextile(fileroot, hex_constraints, equivalence, xorig, yorig, cellsize, randassign):

  dimacs_file = fileroot + '.dim'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence, PeriodicTimeAdjust(1, 0, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  clauses = inflate_grid_template(hex_constraints, grid, G.name)

  # add clauses for a cardinality bounds
  size = max(equivalence.rowsize * equivalence.rowsize // 2 - 40, 0)
  # clauses.extend(bound_population(grid, LessThanOrEqual, size))
  clauses.extend(bound_population(grid, GreaterThanOrEqual, size))

  # assign some random cells to generate a variety of output
  for rep in range(randassign):
    clauses.append((Literal('c_%d_%d_0' %
                            (random.randint(0, root.equivalence.rowsize - 1),
                             random.randint(0, root.equivalence.rowsize - 1))),))

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
  adjust = 0
  if isinstance(equivalence, Tesselated) and isinstance(equivalence.tessellation, FaceCentered):
    adjust = 2
  for i in range(2 * len(valuegrid[0]) - adjust):
    row = []
    for j in range(2 * len(valuegrid[0][0]) - adjust):
      it, jt, _ = root.equivalence.to_equivalent(i, j)
      diagonal = j - i
      if diagonal <= equivalence.rowsize and diagonal > -equivalence.rowsize:
        row.append(valuegrid[0][it][jt])
      else:
        row.append(None)
    cells.append(row)

  draw_hex_cells(xorig, yorig, cells, cellsize)

if __name__ == "__main__":
  randassign = 0
  if len(sys.argv) > 2:
    size = int(sys.argv[2])
  if len(sys.argv) > 3 and sys.argv[3] == 'face':
    tessellation = FaceRotatedRhombus
  else:
    tessellation = RotatedRhombus
  if len(sys.argv) > 4:
    set_solver(sys.argv[4])
  cellsize = 20
  if len(sys.argv) > 5:
    cellsize = int(sys.argv[5])
  if len(sys.argv) > 6:
    randassign = int(sys.argv[6])
  run_hextile(sys.argv[1], HEX_CONSTRAINTS, Tesselated(tessellation(size)), -250, 250, cellsize, randassign)
  input('Press enter to exit.')
