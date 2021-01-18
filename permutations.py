# convert a list of cycles into a permutation mapping
def to_mapping(cycles):
  permutation = {}
  for cycle in cycles:
    n = len(cycle)
    for i in range(n):
      permutation[str(cycle[i])] = str(cycle[(i + 1) % n])
  return permutation

# find the closure of a basis of basis applied to a labeling
def find_closure(basis, labeling):
  all_labelings = set([tuple(labeling)])
  size_was = 0
  inverses = [{v: k for k, v in permutation.items()} for permutation in basis]
  while size_was < len(all_labelings):
    size_was = len(all_labelings)
    for labeling in list(all_labelings):
      for mapping in inverses:
        new_labeling = []
        for from_symbol, to_symbol in labeling:
          new_labeling.append((mapping.get(from_symbol, from_symbol), to_symbol))
        all_labelings.add(tuple(new_labeling))
  return sorted(all_labelings)
