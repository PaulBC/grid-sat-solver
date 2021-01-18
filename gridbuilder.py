from collections import deque
import copy
from tesselation import RotatedRhombus, RotatedSquare, FlippedRectangle

class GridNode(object):
  position = None

  def neighbor_symbols(self):
    pass

  def neighbor(self, symbol):
    pass

  def neighbors(self):
    return [self.neighbor(symbol) for symbol in self.neighbor_symbols()]

  def is_known(self):
    pass

  def name(self):
    pass

  def __str__(self):
    return self.name()

  def __hash__(self):
    return hash(self.position)

  def __eq__(self, other):
    return other.position == self.position

MOORE_DISPLACEMENTS = {
  'N': (-1, 0),
  'NE': (-1, 1),
  'E': (0, 1),
  'SE': (1, 1),
  'S': (1, 0),
  'SW': (1, -1),
  'W': (0, -1),
  'NW': (-1, -1)
}

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
    return '%dX%dt' % (self.rowsize, self.columnsize)

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
  def __init__(self, tesselation):
    self.rowsize = tesselation.rowsize
    self.columnsize = tesselation.columnsize
    self.tesselation = tesselation

  def to_equivalent(self, i, j):
    return self.tesselation.to_grid(i, j)

  def is_outside(self, i, j):
    return False

  def __str__(self):
    return '%dX%d:%s' % (self.rowsize, self.columnsize, self.tesselation.__class__.__name__)


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


class MooreGridNode(GridNode):
  def __init__(self, position, equivalence, timeadjust=PeriodicTimeAdjust(1)):
    self.position = position
    self.equivalence = equivalence
    self.timeadjust = timeadjust
    self.orientation = 0

  def neighbor_symbols(self):
    return ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'G']

  def neighbor(self, symbol):
    i, j, t = self.position
    if symbol == 'G':
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

  def name(self):
    return 'c_%d_%d_%d' % self.position

  def __repr__(self):
    return '%s%s:%s' % (self.name(),
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

def grid_layer(grid, t):
  '''Get layer of grid at generation t, not including outside cells.'''
  return filter(lambda x:x.position[2] == t and not x.is_outside(), grid)
