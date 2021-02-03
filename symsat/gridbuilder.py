from collections import deque
import copy
from .clausebuilder import AbstractLiteral, Literal, ZERO
from .rulesymmetry import NEIGHBOR_LITERALS, N, NE, E, SE, S, SW, W, NW, G
from .symbolic_util import clause_to_string, find_variables, is_comment, parse_line
from .tessellation import RotatedRhombus, RotatedSquare, FlippedRectangle

class GridNode(AbstractLiteral):
  position = None

  def neighbor_symbols(self):
    pass

  def neighbor(self, symbol):
    pass

  def neighbors(self):
    return [self.neighbor(symbol) for symbol in self.neighbor_symbols()]

  def is_known(self):
    pass

  def __str__(self):
    return self.name

  def __hash__(self):
    return hash(self.position)

  def __eq__(self, other):
    return other.position == self.position

  def go(self, *path):
    '''Traverse a path following neighbors (as string values of path items) and return result.'''
    node = self
    for symbol in path:
      node = node.neighbor(str(symbol))
    return node

  # properties for subclasses that use AbstractLiteral
  @property
  def name(self):
    pass

  @property
  def value(self):
    return True

  @property
  def tag(self):
    return None

class Toroidal(object):
  '''An equivalence based on toroidal wrapping.'''
  def __init__(self, rowsize, columnsize, column_shift=0):
    self.rowsize = rowsize
    self.columnsize = columnsize
    self.column_shift = column_shift

  def to_equivalent(self, i, j):
    return (i % self.rowsize,
            (j + self.column_shift * (i // self.rowsize)) % self.columnsize, 0)

  def is_outside(self, i, j):
    return False

  def __str__(self):
    return '%dX%d%st' % (self.rowsize, self.columnsize,
                         '%+d' % self.column_shift if self.column_shift else '')

class Open(object):
  '''An open grid assumed 0 outside bounds.'''
  def __init__(self, rowsize, columnsize):
    self.rowsize = rowsize
    self.columnsize = columnsize

  def to_equivalent(self, i, j):
    return i, j, 0

  def is_outside(self, i, j):
    return i < 0 or i >= self.rowsize or j < 0 or j >= self.columnsize

  def __str__(self):
    return '%dX%do' % (self.rowsize, self.columnsize)

class Strip(object):
  '''A grid wrapped on columns but open on rows.'''
  def __init__(self, rowsize, columnsize):
    self.rowsize = rowsize
    self.columnsize = columnsize

  def to_equivalent(self, i, j):
    return i, j % self.columnsize, 0

  def is_outside(self, i, j):
    return i < 0 or i >= self.rowsize

  def __str__(self):
    return '%dX%do' % (self.rowsize, self.columnsize)

class Tesselated(object):
  def __init__(self, tessellation):
    self.rowsize = tessellation.rowsize
    self.columnsize = tessellation.columnsize
    self.tessellation = tessellation

  def to_equivalent(self, i, j):
    return self.tessellation.to_grid(i, j)

  def is_outside(self, i, j):
    return False

  def __str__(self):
    return '%dX%d:%s' % (self.rowsize, self.columnsize, self.tessellation.__class__.__name__)


class PeriodicTimeAdjust(object):
  def __init__(self, period, ishift=0, jshift=0):
    self.period = period
    self.ishift = ishift
    self.jshift = jshift

  def adjust(self, i, j, t):
    if t == self.period:
      i, j, t = i + self.ishift, j + self.jshift, 0
    return i, j, t

  def __str__(self):
    return 'p%d' % period

CENTER_CELL = Literal('O')

MOORE_DISPLACEMENTS = {k.name: v for k, v in {
  N: (-1, 0),
  NE: (-1, 1),
  E: (0, 1),
  SE: (1, 1),
  S: (1, 0),
  SW: (1, -1),
  W: (0, -1),
  NW: (-1, -1)
}.items()}

# get neighbor symbols as strings.
NEIGHBOR_SYMBOLS = [literal.name for literal in  NEIGHBOR_LITERALS]

class MooreGridNode(GridNode):
  def __init__(self, position, equivalence, timeadjust=PeriodicTimeAdjust(1)):
    self.position = position
    self.equivalence = equivalence
    self.timeadjust = timeadjust
    self.orientation = 0

  def neighbor_symbols(self):
    return NEIGHBOR_SYMBOLS

  def neighbor(self, symbol):
    i, j, t = self.position
    if symbol == G.name:
      i, j, t = self.timeadjust.adjust(i, j, t + 1)
    else:
      di, dj = MOORE_DISPLACEMENTS[symbol]
      i += di
      j += dj
    return self.make_node(i, j, t)

  def make_node(self, i, j, t):
    node = copy.copy(self)
    i, j, node.orientation = self.equivalence.to_equivalent(i, j)
    node.position = i, j, t
    return node

  def grid_range(self, imin, jmin, imax, jmax, t):
    return set(self.make_node(i, j, t) for i in range(imin, imax) for j in range(jmin, jmax))

  def is_outside(self):
    i, j, _ = self.position
    return self.equivalence.is_outside(i, j)

  def is_boundary(self):
    return self.is_outside() and not all([node.is_outside() for node in self.neighbors()])

  def is_known(self):
    return False

  @property
  def name(self):
    return 'c_%d_%d_%d' % self.position

  def __repr__(self):
    return '%s%s:%s' % (self.name,
                      ('(%s)' % self.orientation) if self.orientation else '', self.equivalence)

def build_grid(node):
  '''Build a grid of cells starting with root connected by neighborhod relations.'''
  frontier = deque([node])
  grid_nodes = set(frontier)
  while frontier:
    next_node = frontier.popleft()
    for symbol in next_node.neighbor_symbols():
      neighbor = next_node.neighbor(symbol)
      # expand a node that is not seen already is at standard orientation and not beyond boundary
      if (neighbor not in grid_nodes and neighbor.orientation == 0
          and (not neighbor.is_outside() or neighbor.is_boundary())):
        grid_nodes.add(neighbor)
        frontier.append(neighbor)
  return sorted(grid_nodes, key=lambda node: node.position)

def bound_cardinality(grid, comparator, size, generation, prefix):
  '''Assign a cardinality constraint to a generation, possibly with a variable prefix.'''
  cardinality = comparator([Literal(prefix + node.name)
                            for node in grid_layer(grid, generation)], size)
  clauses = ['Population constraint %s %s' % (comparator.__name__, size)]
  clauses.extend(cardinality.adder_clauses)
  clauses.extend(cardinality.constraint_clauses)
  return clauses

def bound_population(grid, comparator, size, generation = 0):
  '''Assign a cardinality constraint to population in a generation (0 by default).'''
  return bound_cardinality(grid, comparator, size, generation, '')

def bound_helper(grid, comparator, size, name, generation = 0):
  '''Assign a cardinality constraint to helper variable in a generation (0 by default).'''
  return bound_cardinality(grid, comparator, size, generation, name + '$')

def grid_layer(grid, t):
  '''Get layer of grid at generation t, not including outside cells.'''
  return filter(lambda x:x.position[2] == t and not x.is_outside(), grid)

def inflate_grid_template(template_constraints, grid, consequent=None,
                          adjust_tag=lambda orientation, tag: tag,
                          outside_value=ZERO):
  '''Inflate each template clause using grid cells.'''
  def node_info(node):
    return ((outside_value or node).name if node.is_outside() else node.name, node.orientation)

  # collect auxiliary variables (ending with $) to associate with grid cells.
  auxiliary = list(filter(lambda x: x.endswith('$'), find_variables(template_constraints)))

  # map neighbor symbols to names of grid nodes.
  grid_subs = []
  has_zero = False
  for node in grid:
    grid_sub = {sym: node_info(node.neighbor(sym)) for sym in node.neighbor_symbols()}
    grid_sub[CENTER_CELL.name] = node_info(node)
    for variable in auxiliary:
      grid_sub[variable] = (variable + node.name, node.orientation)
    if ZERO.name in [name for name, orientation in grid_sub.values()]:
      has_zero = True
    grid_subs.append(grid_sub)

  # create symbolic clauses for grid nodes using template
  clauses = []
  for constraint in template_constraints:
    if is_comment(constraint):
      clauses.append(constraint)
    else:
      clauses.append('Template: ' + clause_to_string(constraint, consequent))
      # apply the constraint to each grid cell
      for grid_sub in grid_subs:
        clause = []
        for literal in constraint:
          info = grid_sub.get(literal.name)
          if info:
            literal = Literal(info[0], literal.value, adjust_tag(info[1], literal.tag))
          clause.append(literal)
        if ZERO not in clause or ~ZERO not in clause:
          clauses.append(clause)
  if has_zero:
    clauses.append([~ZERO])
  return clauses
