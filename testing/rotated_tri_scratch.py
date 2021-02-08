import random
import sys
import turtle

from symsat.gridbuilder import *
from symsat.tessellation import *
from symsat.clausebuilder import *
from symsat.displayhex import *
from symsat.rulesymmetry import *
from symsat.dimacs_sat import *
from symsat.solver import *
from symsat.tags import *

# The main program here uses a face-centered rotation for the symmetry, so it can be used to generate
# patterns with 120 degree rotational symmetry. It also outputs a complete patch as a hexagon.

# This implements a hex coloring that can be thought of as matching triominos with specific corner
# coloring. Triominoes can be rotated and appear upside down and right side up, constraining
# neighborhoods of adjacent triples of hex cells.

# tags for triomino matching
TRI_TAGS = [
  (1, 2, 3),
  (2, 1, 4),
  (3, 4, 1),
  (4, 3, 2),
  (0, 4, 1),
  (3, 0, 1),
  (0, 3, 2),
  (4, 0, 2),
  (1, 2, 0),
  (2, 1, 0),
]
#tri_0_1_2 tri_0_2_4 tri_0_3_2 tri_0_4_1 tri_0_4_3 tri_1_2_4 tri_1_3_2 tri_1_4_2 tri_1_4_3 tri_2_3_4
TRI_TAGS = [
  (0, 1, 2),
  (0, 2, 4),
  (0, 3, 2),
  (0, 4, 1),
  (0, 4, 3),
  (1, 2, 4),
  (1, 3, 2),
  (1, 4, 2),
  (1, 4, 3),
  (2, 3, 4),
]

LOWER_MATCHES = expand_symmetry(ROTATED_TRI_BELOW, all_tag_tuples((O, W, S), TRI_TAGS))
UPPER_MATCHES = expand_symmetry(ROTATED_TRI_ABOVE, all_tag_tuples((O, E, N), TRI_TAGS))
LOWER_CLAUSES = ['Clauses for lower triomino match'] + make_matching_clauses(LOWER_MATCHES)
UPPER_CLAUSES = ['Clauses for upper triomino match'] + make_matching_clauses(UPPER_MATCHES)
MISC_CLAUSES = expand_symmetry(ROTATED_HEX, parse_lines('''
  # Do not use 0 label when 3-4 cells in straight line.
  #~W(3) ~O(0) ~E(3)
  #~W(4) ~O(0) ~E(4)
  # Rule out trivial 0-1-2 coloring
  #~O(0) ~SW(0) ~NE(0) ~NW(2) ~N(1) ~E(2) ~SE(1) ~S(2) ~W(1)
  ~O(4) ~SW(4) ~NE(4) ~NW(2) ~N(1) ~E(2) ~SE(1) ~S(2) ~W(1)
  '''))

ALL_CLAUSES = LOWER_CLAUSES + UPPER_CLAUSES + MISC_CLAUSES

COLORS =  COLORS = ['#4f1111', '#ffffff', '#ffff4f', '#114f11', '#11114f']

def run_triominoes(fileroot, all_clauses, equivalence, xorig, yorig, randassign, cellsize):

  dimacs_file = fileroot + '.dim'
  tag_file = fileroot + '.tag'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence, PeriodicTimeAdjust(1, 0, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  tag_clauses = inflate_grid_template(all_clauses, grid, G.name, outside_value=None)

  # assign some random cells to generate a variety of output
  for rep in range(randassign):
    tag_clauses.append((Literal('c_%d_%d_0' %
                                (random.randint(0, root.equivalence.rowsize - 1),
                                 random.randint(0, root.equivalence.rowsize - 1)), True, 1),))

  # expand clauses to booleans
  clauses = expand_tag_clauses(tag_clauses)

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)

  # write tag form of clauses
  with open(tag_file, 'w') as out:
    output_symbolic(tag_clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file, random.randint(1, 1 << 32), True)
  valuegrid = get_value_grid('c', results)

  '''
  cells = []
  maxj = 8 * len(valuegrid[0][0]) - 2
  for i in range(4 * len(valuegrid[0]) - 2):
    row = []
    for j in range(maxj):
      it, jt, _ = root.equivalence.to_equivalent(i, j)
      diagonal = j - i
      if j - i // 2 > 0 and j - i // 2 < maxj // 2:
      #if diagonal <= root.equivalence.rowsize and diagonal > -root.equivalence.rowsize:
        row.append(valuegrid[0][it][jt])
      else:
        row.append(None)
    cells.append(row)
  '''
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

  draw_hex_cells(xorig, yorig, cells, cellsize, COLORS)

if __name__ == '__main__':
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])
  rows = 14
  if len(sys.argv) > 3:
    rows = int(sys.argv[3])
  randassign = 0
  if len(sys.argv) > 4:
    randassign = int(sys.argv[4])
  cellsize = 20
  if len(sys.argv) > 5:
    cellsize = int(sys.argv[5])

  #run_triominoes(sys.argv[1], ALL_CLAUSES, Toroidal(rows, rows, -rows//2), -250, 350, randassign, cellsize)
  run_triominoes(sys.argv[1], ALL_CLAUSES, Tesselated(FaceRotatedRhombus(rows)), -250, 350, randassign, cellsize)
  input('Press enter to exit.')
