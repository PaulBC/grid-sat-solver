from symsat.tessellation import *

sym = '.O*'

mapper = RotatedRhombus(4)

for i in range(0, 8):
  print(" ".join(["%s%d" % (sym[mapper.to_grid(i, j)[2]], abs(i - j))  for j in range(0, 8)]))

print()
mapper = RotatedSquare(5)

for i in range(-20, 21):
  print(" ".join(["%s" % mapper.to_grid(i, j)[2] for j in range(-20, 21)]))

mapper = RotatedRhombus(4)

for i in range(0, 10):
  print(" ".join(["%s%s%s" % mapper.to_grid(i, j) for j in range(0, 10)]))

print()


def tostring(i, j, label):
  return '%s%s%s ' % (i, j, '.O*X'[label])

mapper = FaceRotatedRhombus(3)
for i in range(0, 10):
  print(("  " * (10 - i)) + " ".join([tostring(*mapper.to_grid(i, j)) for j in range(0, 10)]))

print()
mapper = FaceRotatedRhombus(3)

uniq = set()
for i in range(0, 10):
  for j in range(0, 10):
     uniq.add(mapper.to_grid(i, j)[:2])

label = 'a'
to_label = {}
for pair in sorted(uniq):
  to_label[pair] = label
  label = chr(ord(label) + 1)

def tostring(i, j, label):
  return '%s%s ' % (to_label[(i, j)], ' O*'[label])

for i in range(0, 10):
  print(("  " * (10 - i)) + "".join([tostring(*mapper.to_grid(i, j)) for j in range(0, 10)]))

print()

mapper = RotatedRhombus(3)

uniq = set()
for i in range(0, 10):
  for j in range(0, 10):
     uniq.add(mapper.to_grid(i, j)[:2])

label = 'a'
to_label = {}
for pair in sorted(uniq):
  to_label[pair] = label
  label = chr(ord(label) + 1)

def tostring(i, j, label):
  return '%s%s ' % (to_label[(i, j)], ' O*'[label])

for i in range(0, 10):
  print(("  " * (10 - i)) + "".join([tostring(*mapper.to_grid(i, j)) for j in range(0, 10)]))

print()
