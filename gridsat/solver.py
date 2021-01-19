import os
from .dimacs_sat import load_results

COMMAND = 'lingeling'

def run_solver(input_file, solution_file, seed=None):
  '''Run the solver (assumed to be lingeling and echo and write solution file).'''
  with open(solution_file, 'w') as solution:
    args = '--seed=%s ' % seed if seed is not None else ''
    cmd = COMMAND + ' ' + args + input_file
    print('Running %s' % cmd)
    print('Writing output to  %s' % solution_file)
    solver = os.popen(cmd)
    while True:
      line = solver.readline()
      if not line:
        break
      print(line.strip())
      solution.write(line)

def solve(input_file, solution_file, seed=None):
  '''Run the solver and load results.'''
  run_solver(input_file, solution_file, seed)
  with open(input_file) as input, open(solution_file) as solution:
    return load_results(input, solution)
