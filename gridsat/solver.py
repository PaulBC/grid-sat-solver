import os
from .dimacs_sat import load_results

COMMAND = 'lingeling %s'

def run_solver(input_file, solution_file):
  with open(solution_file, 'w') as solution:
    cmd = COMMAND % input_file
    print('Running %s' % cmd)
    print('Writing output to  %s' % solution_file)
    solver = os.popen(cmd)
    while True:
      line = solver.readline()
      if not line:
        break
      print(line.strip())
      solution.write(line)

def solve(input_file, solution_file):
  run_solver(input_file, solution_file)
  with open(input_file) as input, open(solution_file) as solution:
    return load_results(input, solution)
