# SymSAT: a Python API for grid-based SAT solving
This repo consists of Python code for creating SAT instances for grid based constraint problems (like Conway's Game of Life oscillators).
"SymSAT" refers to its use of symmetry and symbols in defining these instances. [This thread](https://www.conwaylife.com/forums/viewtopic.php?f=9&t=5001)
describes some of the motivation behind it.


## Quick start

The simplest way to observe what this package does is to run the demo. It requires the SAT solver `lingeling`
to be installed. Solvers `cadical` and `kissat` can be configured to run and it should be possible to use other SAT solvers as
long as they accept DIMACS format. I have tested these instructions on MacOS 10.15.17. They should work in most
environments (Unix or Windows console), though in the latter, it might be necessary to change how lingeling is invoked.

I assume Python 3 throughout, but I have attempted to keep it compatible with Python 2. You must have Python
installed and it must be able to do turtle graphics (which seems to be standard).

From a directory of your choosing:

1. Install lingeling, e.g. by following these instructions: https://www.conwaylife.com/wiki/Tutorials/LLS#Installing_Lingeling
2. Make sure the executable is on your path. E.g. copy the lingeling binary to /usr/local/bin/lingeling or add its location to PATH.
   Verify that `lingeling --help | head` produces truncated help, beginning `usage: lingeling ...`
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

## Overview

The purpose of this code is to generate DIMACS files representing SAT problems as input to an external solver by
providing a more human-readable specification API that includes:
- Symbolic representation of boolean constraints with named variables.
- Parsing of clause `a <- b c d` (b & c & d implies a) as a more readable alternative to equivalent
  `a ~b ~c ~d` (inspired by Prolog `:-` though we are not limited to Horn clauses).
- "Tagged" literals representating small integer values implemented by assigning bits to boolean literals.
  E.g. a(5) means a==5 while ~a(5) means a!=5. Parentheses are used to provide an overloadable python operator (it
  would conflict with hashing to overload equals).
- Generation of cardinality constraints.
- Integration with SAT solvers to solve instances and translate results back. Currently `lingeling`, `cadical`, and `kissat`
  are supported though any solver that accepts DIMACS format should work.
- ~ and () operators for manipulating literals in Python console.
- A template feature for applying a set of constraints (e.g. cellular automata rules or graph coloring rules) to 
  different combinations of variables through substitution. This is supported for grid cells and
  can be used in other ways as well, such as graph adjacency.
- Generation of grids with boundary conditions and symmetry (rotated, cross-surface, open with 0-valued boundaries, etc.)
- Generation of grid constraints (CA rules) with symmetry (rotated, flipped, totalistic, semi-totalistic, etc.)
- Pre-defined Moore neighborhood with compass directions N, NE, E, SE, S, SW, W, NW for neighbors and G (generated)
  for successor state of O (origin)
- Grid templates can include helper variables. E.g. `stator$ <- G O` forces `stator` true if booth cell and successor
  are live. A cardinality bound on stators (one for each cell) could eliminate trivial solutions ($ indicates it
  is part of template and not a single literal).
- Comments in DIMACS file to provide a map of variable names to numbers as well as echoing
  comments from symbolic files.
- Minimally supported turtle graphics to display hex and rhombus grid.
- Minimally supported boolean logic for expanding disjunctions into conjunctions of clauses.

I have attempted some documentation of APIs through docstrings, but there is no user's or developer's guide
thus far. I may add one time permitting.

## Features not implemented yet, but nice to have.
- Simple way to require equality between grid cells (and generate clauses). E.g. this could enforce still-life
  behavior on  part of a Life pattern.
- Positional clauses, i.e. that could enforce that a subset of cell assignments (e.g. representing a glider
  in a collision) are all present relative to some origin that could be expressed by k literals representing
   2^k placements.
- Set grid cell values in initial generation or later (using single-literal clauses).
- Assign region of grid cells using picture format (e.g. using `.` `*` `?`)
- Extensions to syntax, such as expressing cardinality or symmetry in the input file. I have mostly
  avoided this because it is hard to know where to stop, and it is possible to do many of these things
  very concisely in Python.

Note: I am not primarily targeting Conway's Game of Life (CGOL), since there are many competing search applications. 
Right now, I am more interested in laying out tiles with symmetries, hence my focus on which features
to implement.
