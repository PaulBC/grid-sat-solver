import random
import sys
import turtle

from symsat.gridbuilder import *
from symsat.tesselation import *
from symsat.clausebuilder import *
from symsat.displayhex import *
from symsat.rulesymmetry import *
from symsat.dimacs_sat import *
from symsat.solver import *
from symsat.tags import *

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

# base literals for upper and lower triangle around cell
LOWER_TRI = (O, W, S)
UPPER_TRI = (O, E, N)

LOWER_MATCHES = expand_symmetry(ROTATED_TRI_BELOW, all_tag_tuples(LOWER_TRI, TRI_TAGS))
UPPER_MATCHES = expand_symmetry(ROTATED_TRI_ABOVE, all_tag_tuples(UPPER_TRI, TRI_TAGS))
LOWER_CLAUSES = ['Clauses for lower triomino match'] + make_matching_clauses(LOWER_MATCHES)
UPPER_CLAUSES = ['Clauses for upper triomino match'] + make_matching_clauses(UPPER_MATCHES)
PREFER_3_4 = expand_symmetry(ROTATED_HEX, parse_lines('''
  Do not use 0 label when 3-4 cells in straight line.'
  ~W(3) ~O(0) ~E(3)
  ~W(4) ~O(0) ~E(4)
  '''))

ALL_CLAUSES = LOWER_CLAUSES + UPPER_CLAUSES + PREFER_3_4

COLORS =  COLORS = ['darkred', 'white', 'yellow', 'darkgreen', 'darkblue']
COLORS =  COLORS = ['#4f1111', '#ffffff', '#ffff4f', '#114f11', '#11114f']

def run_triomino(fileroot, all_clauses, equivalence, xorig, yorig):

  dimacs_file = fileroot + '.dim'
  tag_file = fileroot + '.tag'
  symbolic_file = fileroot + '.sym'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence, PeriodicTimeAdjust(1, 0, 0))
  grid = build_grid(root)

  # create clauses for life rule conditions on grid
  tag_clauses = inflate_grid_template(all_clauses, grid, G.name)

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
  results = solve(dimacs_file, solution_file, random.randint(1, 1 << 32))
  valuegrid = get_value_grid('c', results)

  cells = []
  for i in range(2 * len(valuegrid[0])):
    row = []
    for j in range(2 * len(valuegrid[0][0])):
      it, jt, _ = root.equivalence.to_equivalent(i, j)
      row.append(valuegrid[0][it][jt])
    cells.append(row)

  turtle.bgcolor('lightblue')
  draw_hex_cells(xorig, yorig, cells, 20, COLORS)

  print()
  print('Hex tile patch with symmetry %s' % equivalence)
  width = len(valuegrid[0])
  for i in range(width):
    print((' ' * (width - i)) + ' '.join([str(cells[i][j]) for j in range(len(valuegrid[0][0]))]))

if __name__ == '__main__':
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])
  rows = 10
  columns = 13
  shift = -5
  if len(sys.argv) > 5:
    rows, columns, shift = map(int, sys.argv[3:6])

  run_triomino(sys.argv[1], ALL_CLAUSES, Toroidal(rows, columns, shift), -250, 350)
  input('Press enter to exit.')
