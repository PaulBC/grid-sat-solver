import sys

from gridbuilder import *
from tesselation import *
from clausebuilder import *
from displayhex import *
from rulesymmetry import *
from dimacs_sat import *
from solver import *

def make_rotated_clauses(clause):
  return all_symmetries(parse_line(clause), ROTATED_HEX)

def make_totalistic_clauses(clause):
  return all_symmetries(parse_line(clause), TOTALISTIC_HEX)

dimacs_file = sys.argv[1] + '.dim'
symbolic_file = sys.argv[1] + '.sym'
solution_file = sys.argv[1] + '.out'

print('# generating clauses for tiling rule')
# birth on 2o
birth_2o = make_rotated_clauses('G <- NW N ~E ~SE ~S ~W')
# survival on 2m
survive_2m_a = make_rotated_clauses('G <- O NW ~N E ~SE ~S ~W')
survive_2m_b = make_rotated_clauses('~G <- ~O NW ~N E ~SE ~S ~W')
# death on 1-, 2o, 2p, 3+
death_le_1 = make_rotated_clauses('~G <- ~N ~E ~SE ~S ~W')
death_2o = make_rotated_clauses('~G <- NW N ~E ~SE ~S ~W')
death_2p = make_rotated_clauses('~G <- NW ~N ~E SE ~S ~W')
death_ge_3 = make_totalistic_clauses('~G <- NW N E')
all_constraints = birth_2o + survive_2m_a + survive_2m_b + death_le_1 + death_2o + death_2p + death_ge_3
print('# done')

# make CA grid
root = MooreGridNode((0, 0, 0), Tesselated(RotatedRhombus(15)), PeriodicTimeAdjust(1, 0, 0))
grid = build_grid(root)

# create clauses for life rule conditions on grid
clauses = inflate_grid_template(all_constraints, grid, G.name)

# add clauses for a cardinality bound of >= 34 in first generation
clauses.extend(bound_population(grid, GreaterThanOrEqual, 34))

# write dimacs file for solver
with open(dimacs_file, 'w') as out:
  output_dimacs(clauses, out)

# write symbolic form of clauses
with open(symbolic_file, 'w') as out:
  output_symbolic(clauses, out)

# solve and print results
results = solve(dimacs_file, solution_file)
valuegrid = get_value_grid('c', results)

cells = []
for i in range(len(valuegrid[0]) * 3):
  row = []
  for j in range(len(valuegrid[0][0]) * 3):
    it, jt, _ = root.equivalence.to_equivalent(i, j)
    row.append(valuegrid[0][it][jt])
  cells.append(row)

draw_hex_cells(-200, 200, cells)

width = len(cells[0])
for i in range(len(cells)):
  print(" " * (width - i), " ".join(['O' if x else '.' for x in cells[i]]))
