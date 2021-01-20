from symsat.tesselation import *

mapper = RotatedRhombus(4)

for i in range(-10, 11):
  print(" ".join(["%s" % mapper.to_grid(i, j)[2] for j in range(-10, 11)]))

print()
mapper = RotatedSquare(5)

for i in range(-20, 21):
  print(" ".join(["%s" % mapper.to_grid(i, j)[2] for j in range(-20, 21)]))

mapper = RotatedRhombus(4)

for i in range(0, 10):
  print(" ".join(["%s%s%s" % mapper.to_grid(i, j) for j in range(0, 10)]))
