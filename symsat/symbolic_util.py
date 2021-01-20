import re
from .clausebuilder import Literal, ZERO
from .tags import expand_tag_clauses

IMPLIED_BY = '<-'

def parse_line(line):
  '''Parse a line of text with symbols.'''
  line = line.strip()
  if not line or line.startswith('# '):
    return line[2:]
  tokens = line.split()
  # if needed, convert 'B <- A0 ... An' to 'B ~AO ... ~An'
  if len(tokens) >= 2 and tokens[1] == IMPLIED_BY:
    return tuple([Literal.parse(tokens[0])] + [~Literal.parse(token) for token in tokens[2:]])

  return tuple(Literal.parse(token) for token in tokens)

def parse_lines(lines):
  return [parse_line(line) for line in lines.strip().split('\n')]

def is_comment(clause):
  '''Check if a symbolic clause is a string comment.'''
  return isinstance(clause, str)

def clause_to_string(clause, consequent):
  '''Convert clause to a string, in implication form if consequent is present.'''
  head = list(filter(lambda x: x.name == consequent, clause))
  if head:
     clause = head + [IMPLIED_BY] + [~x for x in clause if x.name != consequent]
  return ' '.join(map(str, clause))

def find_variables(symbolic_clauses):
  '''Find variables in symbolic clauses.'''
  variables = set()
  for clause in symbolic_clauses:
    if not is_comment(clause):
      for literal in clause:
        variables.add(literal.name)
  return variables
