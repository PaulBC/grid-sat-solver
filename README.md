# grid-sat-solver
Python code for creating SAT instances for grid based constraint problems (like Conway's Game of Life oscillators).
The purpose of this code is to generate DIMACS files representing SAT problems as input to an external solver by
providing a more human-readable specification API that includes:
- Symbolic representation of boolean constraints with named variables.
- Input of clause as `a <- b c d` (b & c & d implies a) as a more readable alternate to equivalent
  `a ~b ~c ~d`.
- "Tagged" literals representating small integer values. E.g. a(5) means a==5 while ~a(5) means a!=5. 
  Parentheses are used to provide an overloadable python operator.
- Generation of cardinality constraints.
- ~ and () operators for manipulating literals in Python console.
- Generation of grids with boundary conditions and symmetry (rotated, cross-surface, open with 0 boundaries, etc.)
- Generation of grid constraints (CA rules) with symmetry.
- Pre-defined Moore neighborhood with compass directions NW, N, NE, E, SE, S, SW, W  for neighbors and G (generated)
  for successor state of O (origin)
- Comments in DIMACS file to provide a map of variable names to numbers as well as echoing
  comments from symbolic files.
- Minimally supported turtle graphics to display hex and rhombus grid.
- Minimally supported boolean logic for expanding disjunctions into conjunctions of clauses.

I have attempted some documentation of APIs through docstrings, but there is no user's or developer's guide
thus far. I may add one time permitting

## Quick start

The simplest way to observe what this package does is to run the demo. It requires the SAT solver `lingeling`
to be installed, though it should be possible to use other SAT solvers as long as they accept DIMACS format.
I have tested these instructions on MacOS 10.15.17. They should work in most environments (Unix or Windows
console), though in the latter, it might be necessary to change how lingeling is invoked.

I assume Python 3 throughout, but I have attempted to keep it compatible with Python 2. You must have Python
installed and it must be able to do turtle graphics (which seems to be standard).

From a directory of your choosing:

1. Install lingeling, e.g. by following these instructions: https://www.conwaylife.com/wiki/Tutorials/LLS#Installing_Lingeling
2. Make sure the executable is on your path. E.g. copy the lingeling binary to /usr/local/bin/lingeling or add its location to PATH.
   Verifiy that `lingeling --help | head` produces truncated help, beginning `usage: lingeling ...`
3. `git clone https://github.com/PaulBC/grid-sat-solver`
4. `cd grid-sat-solver`
5. `python demo.py`

The demo produces a lot of lines to standard output, including echoed lingeling output and the results. It
prompts for enter (or return) each time there is something new to read. It will also open up a window for
turtle graphics.

Note that it creates a directory `data` with all the files generated in this process. These provide examples
of the formats used by this package (both symbolic and dimacs). Comments in the symbolic file are echoed along
to DIMACS so it should be possible (though not necessarily easy) to map the constraints in the final SAT 
problem back to the original specification.
