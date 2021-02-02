import os
from .dimacs_sat import load_results

# Dictionary of solvers by name to command (usually same as name) and whether --seed option works.
SOLVERS = {
  'cadical': ('cadical', True),
  'kissat': ('kissat', False),
  'lingeling': ('lingeling', True)
}

def set_solver(solver):
  global COMMAND
  global SUPPORTS_SEED

  COMMAND, SUPPORTS_SEED = SOLVERS[solver]

def run_solver(input_file, solution_file, seed=None, echo=False):
  '''Run the solver (assumed to be lingeling and echo and write solution file).'''
  with open(solution_file, 'w') as solution:
    args = '--seed=%s ' % seed if seed is not None and SUPPORTS_SEED else ''
    cmd = COMMAND + ' ' + args + input_file
    if echo:
      print('Running %s' % cmd)
      print('Writing output to %s' % solution_file)
    solver = os.popen(cmd)
    while True:
      line = solver.readline()
      if not line:
        break
      if echo:
        print(line.strip())
      solution.write(line)

def solve(input_file, solution_file, seed=None, echo=False):
  '''Run the solver and load results.'''
  run_solver(input_file, solution_file, seed, echo)
  with open(input_file) as input, open(solution_file) as solution:
    return load_results(input, solution)

set_solver('lingeling')
