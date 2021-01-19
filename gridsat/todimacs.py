import sys
from .dimacs_sat import read_symbolic, output_dimacs

with open(sys.argv[1]) as inp:
  clauses = read_symbolic(inp)

with open(sys.argv[2], 'w') as out:
  output_dimacs(clauses, out)

