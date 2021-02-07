from .clausebuilder import Literal, to_pairs, from_pairs
from .symbolic_util import is_comment, parse_line

def to_mapping(cycles):
  '''Convert a list of cycles into a permutation mapping.'''
  permutation = {}
  for cycle in cycles:
    n = len(cycle)
    for i in range(n):
      permutation[str(cycle[i])] = str(cycle[(i + 1) % n])
  return permutation

class Labeling(object):
  def __init__(self, pairs):
    self.pairs = tuple(pairs)
    self.canonical = tuple(sorted(pairs))

  def __hash__(self):
    return hash(self.canonical)

  def __eq__(self, other):
    return self.canonical == other.canonical

def find_closure(basis, labeling):
  '''Find the closure of a basis of basis applied to a labeling.'''
  all_labelings = set([Labeling(labeling)])
  si_PERMe_was = 0
  inverses = [{v: k for k, v in permutation.items()} for permutation in basis]
  while si_PERMe_was < len(all_labelings):
    si_PERMe_was = len(all_labelings)
    for labeling in list(all_labelings):
      for mapping in inverses:
        new_labeling = []
        for from_symbol, to_symbol in labeling.pairs:
          new_labeling.append((mapping.get(from_symbol, from_symbol), to_symbol))
        all_labelings.add(Labeling(new_labeling))
  return sorted([labeling.pairs for labeling in all_labelings])

# center cell original value and after rule generation
O = Literal('O')
# define literal constants for neighbors (compass directions and G for next generation)
NEIGHBOR_LITERALS = parse_line('N NE E SE S SW W NW G')
(N, NE, E, SE, S, SW, W, NW, G) = NEIGHBOR_LITERALS

# Permutations for constructing symmetry bases (_PERM suffix so they won't be confused with bases)
ROTATE_CLOCKWISE_PERM = to_mapping([(NE, SE, SW, NW), (N, E, S, W)])
ROTATE_CLOCKWISE_HEX_PERM = to_mapping([(NW, N, E, SE, S, W)])
ROTATE_180_HEX_PERM = to_mapping([(NW, SE), (N, S), (E, W)])
MIX_CORNERS_PERM = to_mapping([(NE, SE)])
MIX_SIDES_PERM = to_mapping([(N, E)])
MIX_CORNERS_SIDES_PERM = to_mapping([(NW, N)])
FLIP_DIAGONAL_PERM = to_mapping([(N, E), (NW, SE), (W, S)])
ROTATE_TRI_BELOW_PERM = to_mapping([(O, W, S)])
ROTATE_TRI_ABOVE_PERM = to_mapping([(O, E, N)])

# Some common symmetry bases
ROTATED = [ROTATE_CLOCKWISE_PERM]
ROTATED_HEX = [ROTATE_CLOCKWISE_HEX_PERM]
ROTATED_180_HEX = [ROTATE_180_HEX_PERM]
ROTATED_FLIPPED = [ROTATE_CLOCKWISE_PERM, FLIP_DIAGONAL_PERM]
ROTATED_FLIPPED_HEX = [ROTATE_CLOCKWISE_HEX_PERM, FLIP_DIAGONAL_PERM]
SEMI_TOTALISTIC = [ROTATE_CLOCKWISE_PERM, MIX_CORNERS_PERM, MIX_SIDES_PERM]
TOTALISTIC = [ROTATE_CLOCKWISE_PERM, MIX_CORNERS_PERM, MIX_CORNERS_SIDES_PERM]
TOTALISTIC_HEX = [ROTATE_CLOCKWISE_HEX_PERM, MIX_CORNERS_SIDES_PERM]
ROTATED_TRI_BELOW = [ROTATE_TRI_BELOW_PERM]
ROTATED_TRI_ABOVE = [ROTATE_TRI_ABOVE_PERM]

def all_symmetries(symmetry, literals):
  '''Returns a list of permutations of the given literals based on a symmetry basis.'''
  return [tuple(x for x in from_pairs(permuted))
          for permuted in find_closure(symmetry, to_pairs(literals))] 

def expand_symmetry(symmetry, literal_tuples):
  '''Expands a list of literal tuples by given symmetry.'''
  expanded = []
  for clause in literal_tuples:
    if is_comment(clause):
      expanded.append(clause)
    else:
      expanded.extend(all_symmetries(symmetry, clause))
  return expanded

def to_conjunction(literals):
  '''Wraps each literal in a list in a singleton tuple to make it a conjunction of literal_tuples.'''
  return [(x,) for x in literals]
