import os
import sys
from .dimacs_sat import parse_line, output_dimacs
from .solver import solve, set_solver

def solve_and_print(input_file, echo=False, showall=False, seed=None):
  input_root = os.path.splitext(input_file)[0]
  dimacs_file = input_root + '.dim'
  solution_file = input_root + '.out'

  # read clause from input
  with open(input_file) as inp:
    clauses = [parse_line(line) for line in inp]

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file, seed, echo)

  print('Assignments to values are:')
  for key, value in results:
    if key <= '{' and (showall or value):
      print('%s %s' % (key, value))

if __name__ == "__main__":
  if len(sys.argv) > 2:
    set_solver(sys.argv[2])

  seed = int(sys.argv[3]) if len(sys.argv) > 3 else None

  solve_and_print(sys.argv[1], True, seed=seed)
  
