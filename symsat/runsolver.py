import sys
from .dimacs_sat import parse_line, output_dimacs
from .solver import solve, set_solver

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
    if key <= '{':
      print('%s %s' % (key, value))

if __name__ == "__main__":
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])
  solve_and_print(sys.argv[1])
