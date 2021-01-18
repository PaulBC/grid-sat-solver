import sys
from dimacs_sat import parse_line, output_dimacs
from solver import solve

input_file = sys.argv[1]
dimacs_file = sys.argv[1] + '.dim'
solution_file = sys.argv[1] + '.out'

# read clause from input
with open(input_file) as inp:
  clauses = [parse_line(line) for line in inp] 

# write dimacs file for solver
with open(dimacs_file, 'w') as out:
  output_dimacs(clauses, out)

# solve and print results
results = solve(dimacs_file, solution_file)

print('Assignments to values are:')
for name, value in results:
  print('%s = %s' % (name, value))

