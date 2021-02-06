import os
import sys
import time
from shutil import copyfile

from example.hextile import run_hextile
from example.p3ss import run_p3ss
from example.rhombus import run_rhombus
from example.p2patch import run_p2patch
from example.stilllife import run_stilllife
from example.triominoes import run_triominoes, ALL_CLAUSES, TRI_TAGS

from symsat.dimacs_sat import parse_lines
from symsat.gridbuilder import Tesselated, Toroidal, Open
from symsat.rulesymmetry import expand_symmetry, TOTALISTIC, ROTATED_HEX, TOTALISTIC_HEX
from symsat.solver import set_solver
from symsat.runsolver import solve_and_print
from symsat.runtemplated import solve_template_and_print
from symsat.tessellation import CrossSurface, RotatedSquare, RotatedRhombus

if not os.path.exists('data'):
    os.makedirs('data')

if len(sys.argv) > 1:
  set_solver(sys.argv[1])

def wait_for_enter(msg='===== Press [ENTER] or [RETURN] to continue ====='):
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

print('Life constraints template (with totalistic symmetry applied):')
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

STATOR_TEMPLATE = '''
  # stator is true iff two consecutive live generations
  stator$ <- G O
  ~stator$ <- ~G
  ~stator$ <- ~O
'''

print('Adding template for counting stators (two consecutive live cells) in period-2 patch')
print(STATOR_TEMPLATE)
wait_for_enter()
run_p2patch('data/p2patch', LIFE_CONSTRAINTS + parse_lines(STATOR_TEMPLATE),
            Tesselated(RotatedSquare(12)), 0)
print('Found one with no stators ("phoenix" pattern)')
print('Next searching for 4 stators.')
wait_for_enter()
run_p2patch('data/p2patch+4', LIFE_CONSTRAINTS + parse_lines(STATOR_TEMPLATE),
            Tesselated(RotatedSquare(12)), 4)
print('Found one with 4 stators.')
wait_for_enter()

print('Solving ad hoc SAT file on boolean literals.')
file = 'example/knuth_example.sym'
tmpfile = file.replace('example', 'data')
copyfile(file, tmpfile)
print('Input file is %s, which contains:' % file)
with open(file) as inp:
  for line in inp:
    print(line.rstrip())
wait_for_enter()

print('Solve using "python -m symsat.runsolver %s"' % file)
solve_and_print(tmpfile, True)
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

print('Solve using "python -m symsat.runsolver %s"' % file)
solve_and_print(tmpfile, True)
wait_for_enter()

print('Solving templated SAT file on literal with tags')
templatefile = 'example/color.tpl'
subsfile = 'example/color.sub'
tmptemplatefile = templatefile.replace('example', 'data')
copyfile(templatefile, tmptemplatefile)
tmpsubsfile = subsfile.replace('example', 'data')
copyfile(subsfile, tmpsubsfile)
print('Template file is %s, which contains:' % templatefile)
with open(templatefile) as inp:
  for line in inp:
    print(line.rstrip())
wait_for_enter()
print('Substitutions file is %s, which contains:' % subsfile)
with open(subsfile) as inp:
  for line in inp:
    print(line.rstrip())
wait_for_enter()

print('Solve using "python -m symsat.runtemplated %s %s"' % (templatefile, subsfile))
solve_template_and_print(tmptemplatefile, tmpsubsfile, True)
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

run_hextile('data/hex', HEX_CONSTRAINTS, Tesselated(RotatedRhombus(16)), -180, 350)
wait_for_enter()

RHOMBUS_TEMPLATE = '''
# Rhombuses are placed at hex cells with center matching center of upward-pointing triangle.
# Each label i means opposite vertex points 270 - 120i degrees. (0: 270, 1: 150, 2: 30).
# Some rhombus covers shared triangle:
   O(2) N(0) E(1)
# No two rhombuses cover the shared triangle:
  ~O(2) ~N(0)
  ~O(2) ~E(1)
  ~N(0) ~E(1)
'''
print('Rhombus tiling constraints template:')
print(RHOMBUS_TEMPLATE)
wait_for_enter()

RHOMBUS_CONSTRAINTS = parse_lines(RHOMBUS_TEMPLATE)

run_rhombus('data/rhombus', RHOMBUS_CONSTRAINTS, Tesselated(RotatedRhombus(15)), 120, -20)
wait_for_enter()

print('Triomino constraints for hex coloring.')
print('\n'.join(map(str, TRI_TAGS)))
print('See example/triominoes.py for more detailed setup.')
print('Setting up SAT instance and running solver...')
run_triominoes('data/tri', ALL_CLAUSES, Toroidal(14, 15, -7), -300, 20, 12)
wait_for_enter()

print()
print('Demo is complete. See data/ directory for generated files.')

# Just keep pictures up for a little while in case user hit return too many times
time.sleep(5)
