import os
import sys

# A self-contained main program for appending excluded values to DIMACS output.

'''
(python3 -m symsat.runsolver example/knuth_example.sym
 repeat 6 (echo "Next solution:"
           python3 -m symsat.exclude_solution example/knuth_example.sym.dim example/knuth_example.sym.out
           lingeling example/knuth_example.sym.dim > example/knuth_example.sym.out
           python3 -m symsat.fromdimacs --dimacs_in example/knuth_example.sym.dim --dimacs_out example/knuth_example.sym.out))
'''


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
