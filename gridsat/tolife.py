import sys
from .dimacs_sat import get_value_grid, load_results

with open(sys.argv[1]) as input, open(sys.argv[2]) as solution:
  results = load_results(input, solution)

grid = get_value_grid('c', results)

for i in range(len(grid[0])):
  print(''.join(['*' if x else '.' for x in grid[0][i]]))
