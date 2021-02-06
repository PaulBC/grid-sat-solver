from symsat.clausebuilder import Literal, LessThanOrEqual
from symsat.dimacs_sat import output_dimacs, output_symbolic
from symsat.solver import solve

def canonical(i, j, k):
  '''Returns a unique representation of triple (i, j, k) up to rotation.'''
  return min((i, j, k), (j, k, i), (k, i, j))

def tri_literal(i, j, k):
  '''Returns a literal based on canonical form of triple (i, j, k).''' 
  return Literal('tri_%d_%d_%d' % canonical(i, j, k))

def bound_count(literals, comparator, size):
  '''Assign a cardinality constraint.'''
  cardinality = comparator(literals, size)
  clauses = ['Bounded %s %s' % (comparator.__name__, size)]
  clauses.extend(cardinality.adder_clauses)
  clauses.extend(cardinality.constraint_clauses)
  return clauses

fileroot = 'data/triomino'

dimacs_file = fileroot + '.dim'
symbolic_file = fileroot + '.sym'
solution_file = fileroot + '.out'

seen = set()
n = 4
for i in range(n):
  for j in range(n):
    for k in range(n):
      literal = tri_literal(i, j, k)
      if literal not in seen:
        seen.add(literal)

used = set()
clauses = []
for i in range(n):
  for j in range(n):
    if i != j:
      literals = tuple(tri_literal(i, j, k) for k in range(n) if k != i and k != j)
      clauses.append(literals)
      used.update(literals)

clauses.append((tri_literal(0, 1, 2),))
clauses.append((~tri_literal(0, 2, 1),))

clauses.extend(bound_count(sorted(used), LessThanOrEqual, 8))

exclude = True
while exclude:
  # write dimacs file for solver
  with open(dimacs_file, 'w') as out:
    output_dimacs(clauses, out)
  
  # write symbolic form of clauses
  with open(symbolic_file, 'w') as out:
    output_symbolic(clauses, out)
  
  # solve and print results
  results = solve(dimacs_file, solution_file, None, False)
  exclude = tuple(Literal(name, not value) for name, value in results if name < '{')
  clauses.append(exclude)
  if exclude:
    print(" ".join(tuple(name for name, value in results if name < '{' and value)))
