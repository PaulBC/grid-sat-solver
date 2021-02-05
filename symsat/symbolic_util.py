import re
from .clausebuilder import Literal, ZERO

IMPLIED_BY = '<-'

def parse_line(line):
  '''Parse a line of text with symbols.'''
  line = line.strip()
  if not line or line.startswith('#'):
    line = line[1:]
    return line[1:] if line.startswith(' ') else line
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

def inflate_template(template_constraints, substitution_map, consequent=None,
                     adjust_tag=lambda orientation, tag: tag):
  '''Inflate each template clause using substitutions.'''
  # create symbolic clauses for mapped variables using template
  clauses = []
  has_zero = False
  for constraint in template_constraints:
    if is_comment(constraint):
      clauses.append(constraint)
    else:
      clauses.append('Template: ' + clause_to_string(constraint, consequent))
      # apply the constraint to each grid cell
      for substitution in substitution_map:
        clause = []
        for literal in constraint:
          info = substitution.get(literal.name)
          if info:
            literal = Literal(info[0], literal.value, adjust_tag(info[1], literal.tag))
          clause.append(literal)
          if literal.name == ZERO.name:
            has_zero = True
        if not (ZERO in clause and ~ZERO in clause):
          clauses.append(clause)
  if has_zero:
    clauses.append([~ZERO])
  return clauses
