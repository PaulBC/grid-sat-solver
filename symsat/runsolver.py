import sys
from .dimacs_sat import parse_line, output_dimacs
from .solver import solve

def solve_and_print(input_file):
  dimacs_file = input_file + '.dim'
  solution_file = input_file + '.out'

  # read clause from input
  with open(input_file) as inp:
    clauses = [parse_line(line) for line in inp]

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file)

  print('Assignments to values are:')
  for key, value in results:
    if key <= 'z':
      print('%s %s' % (key, value))

if __name__ == "__main__":
  solve_and_print(sys.argv[1])
