class Tessellation(object):
  '''Base class for tessellation of plane into boxes according to symmetry.'''
  def __init__(self, rowsize, columnsize):
    self.rowsize = rowsize
    self.columnsize = columnsize
    self.transformations = {0: lambda i, j: (i, j)}
    self.transformations.update(self._transformations())

  def is_transformed(self, i, j):
    '''Returns whether box (i, j) is transformed from standard orientation.'''
    pass

  def box(self, i, j):
    '''Returns box containing cell coordinates.'''
    return i // self.rowsize, j // self.columnsize

  def recenter(self, i, j, label):
    '''Recenters grid coordinates if necessary (such as for face-centered rotation).'''
    return i, j, label

  def to_grid(self, i, j):
    # loop through transformations
    for label, transformation in self.transformations.items():
       # find transformed (i, j)
      it, jt = transformation(i, j)
      # if the box containing it, jt is not rotated
      if not self.is_transformed(*self.box(it, jt)):
        # use mod function to find the coordinates inside the box and recenter if needed.
        return self.recenter(it % self.rowsize, jt % self.columnsize, label)

class FaceCentered(object):
  '''Overloads recenter method for face-centered rotations.'''
  def recenter(self, i, j, label):
    # adjust to face-centered position so (0, 0) -> (0, 0).
    # Note that we still need vertex-centered rotation to identify boxes.
    di, dj = self.transformations[label](0, 0)
    i -= di
    j -= dj
    # equate corresponding border cells.
    if i == self.rowsize  or j == 0:
      i, j = j, i
    # orientation can be inconsistent, so we don't return it
    return i, j, 0

class RotatedRhombus(Tessellation):
  '''Maps a rhombus to grid boxes with 120 degree vertex-centered rotations.'''
  def __init__(self, size):
    super(RotatedRhombus, self).__init__(size, size)

  def is_transformed(self, i, j):
    return (i + j) % 3 != 0

  def _transformations(self):
    return {
      1: lambda i, j: (-j - 1, i - j),
      2: lambda i, j: (j - i - 1, -i - 1)
    }

class FaceRotatedRhombus(FaceCentered, RotatedRhombus):
  '''Maps a rhombus to grid boxes with 120 degree face-centered rotations.'''
  def __init__(self, size):
    super(FaceRotatedRhombus, self).__init__(size)

class RotatedSquare(Tessellation):
  '''Maps a square to grid boxes with 90 degree vertex-centered rotations.'''
  def __init__(self, size):
    super(RotatedSquare, self).__init__(size, size)

  def is_transformed(self, i, j):
    return i % 2 != 0 or j % 2 != 0

  def _transformations(self):
    return {
      1: lambda i, j: (-j - 1, i),
      2: lambda i, j: (-i - 1, -j - 1),
      3: lambda i, j: (j, -i - 1)
    }

class FaceRotatedSquare(FaceCentered, RotatedSquare):
  '''Maps a square to grid boxes with 90 degree face-centered rotations.'''
  def __init__(self, size):
    super(FaceRotatedSquare, self).__init__(size)

class FlippedRectangle(Tessellation):
  '''Maps a rectangle to grid boxes flipped across orthogonal lines between grid cells.'''
  def __init__(self, rowsize, columnsize):
    super(FlippedRectangle, self).__init__(rowsize, columnsize)

  def is_transformed(self, i, j):
    return i % 2 != 0 or j % 2 != 0

  def _transformations(self):
    return {
      1: lambda i, j: (-1 - i, j),
      2: lambda i, j: (i, -1 - j),
      3: lambda i, j: (-1 - i, -1 - j)
    }

class CenterFlippedRectangle(FlippedRectangle):
  '''Maps a rectangle to grid boxes flipped across orthogonal lines through center of grid cells.'''
  def __init__(self, rowsize, columnsize):
    super(CenterFlippedRectangle, self).__init__(rowsize, columnsize)

  def recenter(self, i, j, label):
    # adjust to face-centered position so (0, 0) -> (0, 0).
    # Note that we still need vertex-centered rotation to identify boxes.
    di, dj = self.transformations[label](0, 0)
    i -= di
    j -= dj
    # orientation can be inconsistent, so we don't return it
    return i, j, 0

class CrossSurface(Tessellation):
  '''Maps a rectangle to grid boxes as cross-surface (reverse order between boundaries).'''
  def __init__(self, rowsize, columnsize):
    super(CrossSurface, self).__init__(rowsize, columnsize)

  def is_transformed(self, i, j):
    return i % 2 != 0 or j % 2 != 0

  def _transformations(self):
    return {
      1: lambda i, j: (i - self.rowsize, self.columnsize - 1 - j),
      2: lambda i, j: (-1 - i, -1 - j),
      3: lambda i, j: (self.rowsize - 1 - i, j - self.columnsize)
    }

