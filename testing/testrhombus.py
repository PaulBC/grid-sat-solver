import sys

from gridsat.clausebuilder import *
from gridsat.dimacs_sat import *
from gridsat.displayhex import *
from gridsat.gridbuilder import *
from gridsat.rulesymmetry import *
from gridsat.solver import *
from gridsat.tags import *
from gridsat.tesselation import *

dimacs_file = sys.argv[1] + '.dim'
symbolic_file = sys.argv[1] + '.sym'
tag_file = sys.argv[1] + '.tag'
solution_file = sys.argv[1] + '.out'

rules = [
# some rhombus covers the center
  (O(2), N(0), E(1)),
# no two rhombuses cover the center
  (~O(2), ~N(0)),
  (~O(2), ~E(1)),
  (~N(0), ~E(1)),
]

# make CA grid
rhombus = RotatedRhombus(11)
root = MooreGridNode((0, 0, 0), Tesselated(rhombus))
#root = MooreGridNode((0, 0, 0), Toroidal(10, 10))
grid = build_grid(root)

def adjust_tag(orientation, tag):
  return (tag - orientation) % 3 if tag < 3 else tag

# create clauses for rhombus packing conditions on grid
tag_clauses = inflate_grid_template(rules, grid, None, adjust_tag)
max_tags = find_max(tag_clauses)

print(inverse_adjust)

# add some random rhombuses to insure non-trival results
import random
random.seed(123)
n = rhombus.columnsize
for i in range(5):
  tag_clauses.append((Literal('c_%d_%d_0' % (random.randint(0, n - 1),
                                             random.randint(0, n - 1)))(random.randint(0,2)),))

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
results = solve(dimacs_file, solution_file)
valuegrid = get_value_grid('c', results)

adjust_back = inverse_adjust(adjust_tag)

cells = []
for i in range(len(valuegrid[0]) * 3):
  row = []
  for j in range(len(valuegrid[0][0]) * 3):
    it, jt, label = root.equivalence.to_equivalent(i, j)
    row.append(adjust_back(label, valuegrid[0][it][jt]))
  cells.append(row)
draw_rhombus_cells(-200, 200, cells)

for row in cells:
  print(" ".join(str(x) if x is not None else '.' for x in row))
