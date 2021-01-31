This directory contains the main distribution, primarily consisting on modules that can be imported.
There are three main programs, `todimacs`, `fromdimacs`, and `runsolver` that can be invoked as modules, e.g.:

`python -m symsat.runsolver example/coloring.sym`

The code in `tessellation.py` provides ways of dividing up the plane into copies of a finite subset of
cells that are repeated periodically, sometimes rotated or reflected. Some of this is counterintuitive, such
as the rotation of hexagonal grids in integer coordinates. It is presented in more detail in this
[Conway's Game of Life thread](https://www.conwaylife.com/forums/viewtopic.php?f=12&t=5019).
