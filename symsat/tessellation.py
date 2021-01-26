class Tessellation(object):
  def __init__(self, rowsize, columnsize):
    self.rowsize = rowsize
    self.columnsize = columnsize
    self.transformations = {0: lambda i, j: (i, j)}
    self.transformations.update(self._transformations())

  def is_transformed(self, i, j):
    pass

  def box(self, i, j):
    return i // self.rowsize, j // self.columnsize

  def to_grid(self, i, j):
    # loop through transformations
    for label, transformation in self.transformations.items():
       # find transformed (i, j)
      it, jt = transformation(i, j)
      # if the box containing it, jt is not rotated
      if not self.is_transformed(*self.box(it, jt)):
        # use mod function to find the coordinates inside the box
        return it % self.rowsize, jt % self.columnsize, label

class RotatedRhombus(Tessellation):
  def __init__(self, size):
    super(RotatedRhombus, self).__init__(size, size)

  def is_transformed(self, i, j):
    return (i + j) % 3 != 0

  def _transformations(self):
    return {
      1: lambda i, j: (-j - 1, i - j),
      2: lambda i, j: (j - i - 1, -i - 1)
    }

class RotatedSquare(Tessellation):
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

class FlippedRectangle(Tessellation):
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

class CrossSurface(Tessellation):
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

