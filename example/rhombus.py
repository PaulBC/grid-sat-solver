import random
import sys

from symsat.clausebuilder import *
from symsat.dimacs_sat import *
from symsat.displayhex import *
from symsat.gridbuilder import *
from symsat.rulesymmetry import *
from symsat.solver import *
from symsat.tags import *
from symsat.tesselation import *

RHOMBUS_CONSTRAINTS = parse_lines('''
# Rhombuses are placed at hex cells with center matching center of upward-pointing triangle.
# Each label i means opposite vertex points 270 - 120i degrees. (0: 270, 1: 150, 2: 30).
# Some rhombus covers shared triangle:
   O(2) N(0) E(1)
# No two rhombuses cover the shared triangle:
  ~O(2) ~N(0)
  ~O(2) ~E(1)
  ~N(0) ~E(1)
''')

def run_rhombus(fileroot, rhombus_constraints, equivalence, xorig, yorig):
  dimacs_file = fileroot + '.dim'
  symbolic_file = fileroot + '.sym'
  tag_file = fileroot + '.tag'
  solution_file = fileroot + '.out'

  # make CA grid
  root = MooreGridNode((0, 0, 0), equivalence)
  grid = build_grid(root)

  def adjust_tag(orientation, tag):
    return (tag - orientation) % 3 if tag < 3 else tag

  # create clauses for rhombus packing conditions on grid
  tag_clauses = inflate_grid_template(rhombus_constraints, grid, None, adjust_tag)
  max_tags = find_max(tag_clauses)

  print(inverse_adjust)

  # add some rhombuses to ensure non-trival results
  n = root.equivalence.rowsize
  tag_clauses.append((Literal('c_1_1_0')(0),))
  tag_clauses.append((Literal('c_3_5_0')(1),))
  tag_clauses.append((Literal('c_7_2_0')(2),))
  tag_clauses.append((Literal('c_5_7_0')(0),))
  tag_clauses.append((Literal('c_9_7_0')(1),))
  tag_clauses.append((Literal('c_3_11_0')(2),))
  tag_clauses.append((Literal('c_%d_%d_0' % (n // 2 - 3, n - 1) )(1),))
  tag_clauses.append((Literal('c_%d_%d_0' % (n // 2 + 3, n - 1) )(1),))
  tag_clauses.append((Literal('c_%d_%d_0' % (n - 1, n // 2 - 3) )(0),))
  tag_clauses.append((Literal('c_%d_%d_0' % (n - 1, n // 2 + 2) )(0),))

  clauses = expand_tag_clauses(tag_clauses)

  clauses = expand_tag_clauses(tag_clauses)

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(tag_clauses, out)

  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)

  # write tag form of clauses
  with open(tag_file, 'w') as out:
    output_symbolic(tag_clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file, random.randint(1, 1 << 32))
  valuegrid = get_value_grid('c', results)

  adjust_back = inverse_adjust(adjust_tag)

  cells = []
  for i in range(len(valuegrid[0])):
    row = []
    for j in range(len(valuegrid[0][0])):
      it, jt, label = root.equivalence.to_equivalent(i, j)
      row.append(adjust_back(label, valuegrid[0][it][jt]))
    cells.append(row)
  draw_rhombus_cells(xorig, yorig, cells)

  print()
  print('Rhombus tiling patch with symmetry %s' % equivalence)
  width = len(cells[0])
  for i in range(len(cells)):
    print((' ' * (width - i))  + ' '.join(str(x) if x is not None else '.' for x in cells[i]))

if __name__ == "__main__":
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])
  run_rhombus(sys.argv[1], RHOMBUS_CONSTRAINTS, Tesselated(RotatedRhombus(15)), -100, 100)
  input('Press enter to exit.')
