import argparse
import sys
from .clausebuilder import Literal
from .dimacs_sat import get_value_grid, load_results
from .displayhex import draw_hex_cells, draw_rhombus_cells

# parse changes to defaults
parser = argparse.ArgumentParser()
parser.add_argument('--dimacs_in', required=True, help='DIMACS input file containing clauses.')
parser.add_argument('--dimacs_out', required=True, help='DIMACS output file containing solution.')
parser.add_argument('--format', default='list',
                    choices=['list', 'life', 'hex', 'hex_numeric',
                             'hex_turtle', 'rhombus_turtle', 'exclude'],
                    help='Format to ouput solution.')
parser.add_argument('--hex_size', type=int, default=20, help='Size of hex or rhombus for turtle.')
args = parser.parse_args()

def wait_for_enter(msg='===== Press [ENTER] or [RETURN] to continue ====='):
  '''Wait for user to hit enter before proceeding.'''
  # Use input() but catch exception to be compatible with Python 2 and 3.
  try:
    input(msg)
  except:
    pass

def output_list(results):
  '''Output list of results as names and values, one per line.'''
  for key, value in results:
    if key <= '{':
      print('%s %s' % (key, value))

def output_life(results):
  '''Output results in as a Game of Life picture that can be copied into (e.g.) Golly.'''
  grid = get_value_grid('c', results)

  for i in range(len(grid[0])):
    print(''.join(['*' if x else '.' for x in grid[0][i]]))

# default symbols used for hex values
HEX_SYMBOLS = '.O*'
def hex_symbol(symbols, value):
  return symbols[value] if value < len(symbols) else str(value)

def output_hex(results, symbols = HEX_SYMBOLS):
  '''Output results using character symbols, skewed as a rhombic section of a hex grid.'''
  grid = get_value_grid('c', results)
  width = len(grid[0][0])

  for i in range(len(grid[0])):
    print((' ' * (width - i)) + ' '.join([hex_symbol(symbols, x) for x in grid[0][i]]))

def output_hex_numeric(results):
  '''Output results using numbers, skewed as a rhombic section of a hex grid.'''
  output_hex(results, '')

def output_hex_turtle(results, xorig=-100, yorig=100):
  '''Draw hex grid with turtle graphics.'''
  grid = get_value_grid('c', results)
  cells = []
  for i in range(len(grid[0])):
    row = []
    for j in range(len(grid[0][0])):
      row.append(grid[0][i][j])
    cells.append(row)
  draw_hex_cells(xorig, yorig, cells, args.hex_size)
  wait_for_enter()

def output_rhombus_turtle(results, xorig=-100, yorig=100):
  '''Draw rhombus grid with turtle graphics.'''
  grid = get_value_grid('c', results)
  cells = []
  for i in range(len(grid[0])):
    row = []
    for j in range(len(grid[0][0])):
      row.append(grid[0][i][j])
    cells.append(row)
  draw_rhombus_cells(xorig, yorig, cells, args.hex_size)
  wait_for_enter()

def output_exclude(results):
  '''Output a symbolic clause in which each literal is a complementary value to solution,
     which can be added to symbolic SAT instance to rule it out.'''
  print(' '.join([str(Literal(name, isinstance(value, bool) and not value,
                              value if not isinstance(value, bool) else None))
                  for name, value in results if name <= '{']))

if __name__ == "__main__":
  # get results
  with open(args.dimacs_in) as inp, open(args.dimacs_out) as solution:
    results = load_results(inp, solution)

  # output results in selected format
  locals()['output_' + args.format](results)
