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
  size_was = 0
  inverses = [{v: k for k, v in permutation.items()} for permutation in basis]
  while size_was < len(all_labelings):
    size_was = len(all_labelings)
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

# Permutations for constructing symmetry bases
ROTATE_CLOCKWISE = to_mapping([(NE, SE, SW, NW), (N, E, S, W)])
ROTATE_CLOCKWISE_HEX = to_mapping([(NW, N, E, SE, S, W)])
MIX_CORNERS = to_mapping([(NE, SE)])
MIX_SIDES = to_mapping([(N, E)])
MIX_CORNERS_SIDES = to_mapping([(NW, N)])
FLIP_DIAGONAL = to_mapping([(N, E), (NW, SE), (W, S)]) 
ROTATE_TRI_BELOW = to_mapping([(O, W, S)])
ROTATE_TRI_ABOVE = to_mapping([(O, E, N)])

# Some common symmetry bases
ROTATED = [ROTATE_CLOCKWISE]
ROTATED_HEX = [ROTATE_CLOCKWISE_HEX]
ROTATED_FLIPPED = [ROTATE_CLOCKWISE, FLIP_DIAGONAL]
ROTATED_FLIPPED_HEX = [ROTATE_CLOCKWISE_HEX, FLIP_DIAGONAL]
SEMI_TOTALISTIC = [ROTATE_CLOCKWISE, MIX_CORNERS, MIX_SIDES]
TOTALISTIC = [ROTATE_CLOCKWISE, MIX_CORNERS, MIX_CORNERS_SIDES]
TOTALISTIC_HEX = [ROTATE_CLOCKWISE_HEX, MIX_CORNERS_SIDES]
ROTATED_TRI_BELOW = [ROTATE_TRI_BELOW]
ROTATED_TRI_ABOVE = [ROTATE_TRI_ABOVE]

def all_symmetries(symmetry, literals):
  '''Returns a list of permutations of the given literals based on a symmetry basis.'''
  return [tuple(x for x in from_pairs(permuted))
          for permuted in find_closure(symmetry, to_pairs(literals))] 

def expand_symmetry(symmetry, clauses):
  '''Expands a list of clauses by given symmetry.'''
  expanded = []
  for clause in clauses:
    if is_comment(clause):
      expanded.append(clause)
    else:
      expanded.extend(all_symmetries(symmetry, clause))
  return expanded

def to_conjunction(literals):
  '''Wraps each literal in a list in a singleton tuple to make it a conjunction of clauses.'''
  return [(x,) for x in literals]
