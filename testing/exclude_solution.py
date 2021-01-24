import os
import sys

# repeat 500 (python3 -m testing.exclude_solution data/tri.dim data/tri.out ; kissat data/tri.dim > data/tri.out ; python -m symsat.fromdimacs --dimacs_in data/tri.dim --dimacs_out data/tri.out --format hex )

input = sys.argv[1]
solution = sys.argv[2]
tmp_out = input + '.tmp'

with open(tmp_out, 'w') as out:
  with open(input) as inp:
    for line in inp:
      if line.startswith('p cnf'):
        toks = line.split()
        out.write(' '.join(toks[:-1]) + ' ' + str(int(toks[-1]) + 1) + '\n')
      else:
        out.write(line)

  out.write('c excluded solution:\n')
  with open(solution) as inp:
    for line in inp:
      toks = line.split()
      if toks[0] == 'v':
        inverse = [str(-int(x)) for x in toks[1:]]
        out.write(' '.join(inverse) + '\n')

os.replace(tmp_out, input)
