import argparse
import sys
from .dimacs_sat import get_value_grid, load_results

# parse changes to defaults
parser = argparse.ArgumentParser()
parser.add_argument('--dimacs_in', required=True, help='DIMACS input file containing clauses.')
parser.add_argument('--dimacs_out', required=True, help='DIMACS output file containing solution.')
parser.add_argument('--format', default='list', choices=['list', 'life', 'hex', 'numeric_hex'],
                    help='Format to ouput solution.')
parser.add_argument('--numeric_hex', action='store_true')
args = parser.parse_args()

def output_list(results):
  for key, value in results:
    if key <= 'z':
      print('%s %s' % (key, value))

def output_life(results):
  grid = get_value_grid('c', results)

  for i in range(len(grid[0])):
    print(''.join(['*' if x else '.' for x in grid[0][i]]))

# default symbols used for hex values
HEX_SYMBOLS = '.O*'
def hex_symbol(symbols, value):
  return symbols[value] if value < len(symbols) else str(value)

def output_hex(results, symbols = HEX_SYMBOLS):
  grid = get_value_grid('c', results)
  width = len(grid[0][0])

  for i in range(len(grid[0])):
    print((' ' * (width - i)) + ' '.join([hex_symbol(symbols, x) for x in grid[0][i]]))

def output_numeric_hex(results):
  output_hex(results, '')

# get results
with open(args.dimacs_in) as input, open(args.dimacs_out) as solution:
  results = load_results(input, solution)

# output results in selected format
locals()['output_' + args.format](results)
