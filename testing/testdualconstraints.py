import sys

from gridsat.gridbuilder import *
from gridsat.tesselation import *
from gridsat.clausebuilder import *
from gridsat.rulesymmetry import *
from gridsat.dimacs_sat import *

# This represents Life rules as a disjunction of conjunctions and flattens them into clauses.

def make_clauses(clause):
  return flatten_disjunction(list(map(to_conjunction, all_symmetries(TOTALISTIC, parse_line(clause)))))

grid = build_grid(MooreGridNode((0, 0, 0), Open(5, 16), PeriodicTimeAdjust(3, 1, 0)))

print('# generating conjunctions for CA rule')
lt2 = make_clauses('~G ~N ~NE ~E ~SE ~S ~SW ~W')
ge4 = make_clauses('~G N NE E SE')
eq3 = make_clauses('G ~N ~NE ~E ~SE ~S SW W NW')
eq2a = make_clauses('O G ~N ~NE ~E ~SE ~S ~SW W NW')
eq2b = make_clauses('~O ~G ~N ~NE ~E ~SE ~S ~SW W NW')
all_constraints = flatten_disjunction([lt2, ge4, eq3, eq2a, eq2b])
print('# done')

clauses = inflate_grid_template(all_constraints, grid)

clauses.append(parse_line('c_3_3_0'))

with open('%s.dim' % sys.argv[1], 'w') as out:
  output_dimacs(clauses, out)

with open('%s.sym' % sys.argv[1], 'w') as out:
  output_symbolic(clauses, out)
