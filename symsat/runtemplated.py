import os
import sys
from .dimacs_sat import parse_line, output_dimacs, output_symbolic
from .solver import solve, set_solver
from .symbolic_util import to_substitution_map, inflate_template

def solve_template_and_print(template_file, substitution_file, echo=False):
  input_root = os.path.splitext(substitution_file)[0] 
  symbolic_file = input_root + '.sym'
  dimacs_file = input_root + '.dim'
  solution_file = input_root + '.out'

  # read template from input
  with open(template_file) as template:
    template_clauses = [parse_line(line) for line in template]

  # read substitutions from imput
  with open(substitution_file) as substitutions:
    substitution_map = to_substitution_map([line.split()
                                           for line in [line.strip() for line in substitutions]
                                           if line and not line.startswith('#')])

  clauses = inflate_template(template_clauses, substitution_map)

  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)

  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)

  # solve and print results
  results = solve(dimacs_file, solution_file, None, echo)

  print('Assignments to values are:')
  for key, value in results:
    if key <= '{':
      print('%s %s' % (key, value))

if __name__ == "__main__":
  if len(sys.argv) > 3:
    set_solver(sys.argv[3])
  solve_template_and_print(sys.argv[1], sys.argv[2], True)
