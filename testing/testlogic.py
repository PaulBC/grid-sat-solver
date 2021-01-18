from clausebuilder import *
from rulesymmetry import *
from dimacs_sat import *
from tags import *
from collections import defaultdict
from functools import reduce

a = Literal('a')
b = Literal('b')
c = Literal('c')
x = Literal('x')

match1 = [a(5), b(3), c(2), x]
match2 = [a(0), b(1), c(6), ~x]
match3 = [a(7), b(2), c(4), x]
match4 = [a(3), b(2), c(1), ~x]

max_values = find_max([match1, match2, match3, match4])

clauses1 = match_integers_all(match1, max_values)
clauses2 = match_integers_all(match2, max_values)
clauses3 = match_integers_all(match3, max_values)
clauses4 = match_integers_all(match4, max_values)

clauses12 = remove_redundant(expand_disjunction(clauses1, clauses2))
clauses123 = remove_redundant(expand_disjunction(clauses12, clauses3))
clauses123 = remove_redundant(expand_disjunction(clauses123, clauses4))

for clause in clauses123:
  print(' '.join(map(str, clause)))

card = GreaterThanOrEqual([Literal(x) for x in 'a b c d e f g h'.split()], 5)
print('# clauses')
for clause in card.adder_clauses:
  print(' '.join(map(str, clause)))
print()

print('# constraint')
for clause in card.constraint_clauses:
  print(' '.join(map(str, clause)))
print()

card = LessThanOrEqual([Literal(x) for x in 'a b c d e f g h'.split()], 5)
print('# clauses')
for clause in card.adder_clauses:
  print(' '.join(map(str, clause)))
print()

print('# constraint')
for clause in card.constraint_clauses:
  print(' '.join(map(str, clause)))
print()

print('# clauses for number matching')

syms = all_symmetries((O(1), N(2), W(0), S(3)), ROTATED_TRI_BELOW)

disjunction = make_or_of_ands_matcher(syms)

for x in flatten_disjunction(disjunction):
  print(' '.join(map(str, x)))
print()

def to_python(clause):
  return "(" + " or ".join(('%s' if x.value else '(not %s)') % x.name.replace('#', '_') for x in clause) + ') and'

print('# rhombus fitting rules')
rules = '''W(2) O(1) S(0)
  ~W(2) ~O(1)
  ~W(2) ~S(0)
  ~O(1) ~S(0)
  ~W(3)
  ~O(3)
  ~S(3)'''
clauses = [parse_line(rule) for rule in rules.split('\n')]
maxv = find_max(clauses)

print(sorted(clauses[0]))
print(sorted(match_integers_all(clauses[0], maxv)))


all_clauses = []
for clause in clauses:
  all_clauses.extend(match_integers_any(clause, maxv))

print('# true tuples for this rule')
for x in sorted(find_true_tuples(all_clauses)):
  print('# ' + str([y.value for y in x]))

print('# matching integers')
nlits = [Literal.parse(x) for x in "~x(11) ~y(7) ~z(5)".split()]
x, y, z = [~x for x in nlits]
maxv = find_max([(x, y, z)])
print(x, y, z)
print(match_integers_all([x, ~y, z], maxv))


print('# clauses for triomino matching')
TRIS = [
  (1, 2, 3),
  (2, 1, 4),
  (3, 4, 1),
  (4, 3, 2),
  (0, 4, 1),
  (3, 0, 1),
  (0, 3, 2),
  (4, 0, 2),
  (1, 2, 0),
  (2, 1, 0),
]

literals = [O, S, W]

matchers = []
for tri in TRIS:
  matchers.extend(all_symmetries(tuple(x(tag) for x, tag in zip(literals, tri)),
                                ROTATED_TRI_BELOW))

clauses = make_matching_clauses(matchers)

for clause in sorted(clauses):
  print(" ".join(map(str, clause)))

print(len(clauses))

maxtags = find_max(clauses)
print('# boolean clauses for triomino matching')
sat = []
for clause in sorted(clauses):
  sat.extend(match_integers_any(clause, maxtags))
for literal in [O, S, W]:
  sat.extend(less_than(literal, 5))

for x in sat:
  print(" ".join(map(str, x)))

