import os
from shutil import copyfile

from example.hextile import run_hextile
from example.p3ss import run_p3ss
from example.rhombus import run_rhombus
from example.stilllife import run_stilllife

from gridsat.dimacs_sat import parse_lines
from gridsat.gridbuilder import Tesselated, Toroidal, Open
from gridsat.rulesymmetry import expand_symmetry, TOTALISTIC, ROTATED_HEX, TOTALISTIC_HEX
from gridsat.runsolver import solve_and_print
from gridsat.tesselation import CrossSurface, RotatedSquare, RotatedRhombus

if not os.path.exists('data'):
    os.makedirs('data')

def wait_for_enter(msg='**** Press [ENTER] or [RETURN] to continue ****'):
  '''Wait for user to hit enter before proceeding.'''
  # Use input() but catch exception to be compatible with Python 2 and 3.
  try:
    input(msg)
  except:
    pass

LIFE_TEMPLATE = '''
  # death by loneliness or crowding
  ~G <- ~N ~NE ~E ~SE ~S ~SW ~W
  ~G <- N NE E SE
  # birth on 3 neighbors
   G <- N NE E ~SE ~S ~SW ~W ~NW
  # survival on 2 or 3 neighbors
  ~G <- ~O N NE ~E ~SE ~S ~SW ~W ~NW
   G <- O N NE ~E ~SE ~S ~SW ~W ~NW
'''

print('Life constraints template:')
print(LIFE_TEMPLATE)
wait_for_enter()

LIFE_CONSTRAINTS = expand_symmetry(TOTALISTIC, parse_lines(LIFE_TEMPLATE))

run_stilllife('data/still_rotated', LIFE_CONSTRAINTS, Tesselated(RotatedSquare(10)))
wait_for_enter()

run_stilllife('data/still_cross_surface', LIFE_CONSTRAINTS, Tesselated(CrossSurface(10, 10)))
wait_for_enter()

run_stilllife('data/still_open', LIFE_CONSTRAINTS, Open(10, 10))
print('(i.e. stabilized at boundaries)')
wait_for_enter()

print('Setting up search for p3 spaceship.')
run_p3ss('data/p3ss', LIFE_CONSTRAINTS)
wait_for_enter()

HEX_ROTATED_TEMPLATE = '''
  # birth on 2o
   G <- NW N ~E ~SE ~S ~W
  # survival on 2m
   G <- O NW ~N E ~SE ~S ~W
  ~G <- ~O NW ~N E ~SE ~S ~W
  # death on <=1, 2o, 2p
  ~G <- ~N ~E ~SE ~S ~W
  ~G <- NW N ~E ~SE ~S ~W
  ~G <- NW ~N ~E SE ~S ~W
'''

HEX_TOTALISTIC_TEMPLATE = '''
  # death on >= 3
  ~G <- NW N E
'''
print('Hex tiling constraints template:')
print('Rotated:')
print(HEX_ROTATED_TEMPLATE)
print('Totalistic:')
print(HEX_TOTALISTIC_TEMPLATE)
wait_for_enter()

HEX_CONSTRAINTS = expand_symmetry(ROTATED_HEX, parse_lines(HEX_ROTATED_TEMPLATE))
HEX_CONSTRAINTS.extend(expand_symmetry(TOTALISTIC_HEX, parse_lines(HEX_TOTALISTIC_TEMPLATE)))

run_hextile('data/hex', HEX_CONSTRAINTS, Tesselated(RotatedRhombus(15)), -250, 350)
wait_for_enter()

RHOMBUS_TEMPLATE = '''
# some rhombus covers the center
   O(2) N(0) E(1))
# no two rhombuses cover the center
  ~O(2) ~N(0))
  ~O(2) ~E(1))
  ~N(0) ~E(1))
'''
print('Rhombus tiling constraints template:')
print(RHOMBUS_TEMPLATE)
wait_for_enter()

RHOMBUS_CONSTRAINTS = parse_lines(RHOMBUS_TEMPLATE)

run_rhombus('data/rhombus', RHOMBUS_CONSTRAINTS, Tesselated(RotatedRhombus(10)), 50, 0)
wait_for_enter()

print('Solving ad hoc SAT file on literal with tags')
file = 'example/coloring.sym'
tmpfile = file.replace('example', 'data')
copyfile(file, tmpfile)
print('Input file is %s, which contains:' % file)
with open(file) as inp:
  for line in inp:
    print(line.rstrip())
wait_for_enter()

print('Solve using "python -m gridsat runsolver %s"' % file)
solve_and_print(tmpfile)
