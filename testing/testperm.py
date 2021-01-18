from rulesymmetry import *
from clausebuilder import Literal, to_pairs, from_pairs

neighborhood = (O, ~G, N(1), NE(2), ~E(3), SE(4), S(5), SW(6), W(7), NW(8))

for x in find_closure(ROTATED_HEX, to_pairs(neighborhood)):
  print(from_pairs(x))
print

for x in find_closure(ROTATED_FLIPPED_HEX, to_pairs(neighborhood)):
  print(from_pairs(x))
print

for x in find_closure(ROTATED, to_pairs(neighborhood)):
  print(from_pairs(x))
print

for x in find_closure(ROTATED_FLIPPED, to_pairs(neighborhood)):
  print(from_pairs(x))
print

cls = find_closure(SEMI_TOTALISTIC, to_pairs(neighborhood))
print(len(cls))

cls = find_closure(TOTALISTIC_HEX, to_pairs(neighborhood))
print(len(cls))

#cls = find_closure(TOTALISTIC, to_pairs(neighborhood))
#print(len(cls))

print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, N, NE, E, SE, S, SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, NE, E, SE, S, SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, E, SE, S, SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, SE, S, SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, ~SE, S, SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, ~SE, ~S, SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, ~SE, ~S, ~SW, W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, ~SE, ~S, ~SW, ~W, NW)))))
print(len(find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, ~SE, ~S, ~SW, ~W, ~NW)))))

for labeling in find_closure(TOTALISTIC, to_pairs((O, ~G, ~N, ~NE, ~E, ~SE, S, SW, W, NW))):
  print(' '.join(map(str, from_pairs(labeling))))
