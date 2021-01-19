import sys
from dimacs_sat import load_results

with open(sys.argv[1]) as input, open(sys.argv[2]) as solution:
  results = load_results(input, solution)

for key, value in results:
  if key <= 'z':
    print(key, value)
