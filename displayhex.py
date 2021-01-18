from math import cos, sin, radians
import turtle

UNITLENGTH = 15

# in other words, sqrt(3)/2 and 1/2, but this makes the purpose clearer.
XSCALE = cos(radians(60))
YSCALE = sin(radians(60))

# a stack to restore state after drawing
TURTLE_STACK = []

def position(i, j):
  return (j - i * XSCALE) * UNITLENGTH, -i * UNITLENGTH * YSCALE

def push_state():
  TURTLE_STACK.append((turtle.position(), turtle.heading(), turtle.isdown()))

def pop_state():
  (position, heading, isdown) = TURTLE_STACK.pop()
  turtle.penup()
  turtle.setposition(*position)
  turtle.setheading(heading)
  if isdown:
    turtle.pendown()
  else:
    turtle.penup()

def draw_hex(fillcolor=None):
  push_state()
  if fillcolor:
    turtle.fillcolor(fillcolor)
  side = UNITLENGTH * XSCALE / YSCALE
  turtle.penup()
  turtle.left(90)
  turtle.forward(side)
  turtle.right(120)
  turtle.pendown()
  if fillcolor:
    turtle.begin_fill()
  for i in range(6):
    turtle.forward(side)
    turtle.right(60)
  if fillcolor:
    turtle.end_fill()
  pop_state()

def draw_rhombus(rotation, fillcolor=None):
  push_state()
  if fillcolor:
    turtle.fillcolor(fillcolor)
  turtle.penup()
  turtle.left(90)
  turtle.right(rotation)
  turtle.forward(UNITLENGTH * XSCALE / YSCALE)
  turtle.right(150)
  side = UNITLENGTH
  turtle.pendown()
  if fillcolor:
    turtle.begin_fill()
  for i in range(2):
    turtle.forward(side)
    turtle.right(60)
    turtle.forward(side)
    turtle.right(120)
  if fillcolor:
    turtle.end_fill()
  turtle.penup()
  pop_state()

RHOMBUS_COLORS = ['lightblue', 'firebrick', 'lightgreen']
def rhombus_cell(i, j, rotation):
  push_state()
  (x, y) = position(i, j)
  turtle.setposition(turtle.xcor() + x, turtle.ycor() + y)
  draw_rhombus(rotation * 120, RHOMBUS_COLORS[rotation])
  pop_state()

def draw_rhombus_cells(xorigin, yorigin, cells):
  turtle.tracer(0, 0)
  turtle.hideturtle()
  turtle.speed(0)
  push_state()
  turtle.penup()
  turtle.setposition(xorigin, yorigin)
  for i in range(len(cells)):
    for j in range(len(cells[i])):
      if cells[i][j] is not None:
        rhombus_cell(i, j, cells[i][j])
  pop_state()
  turtle.update()

HEX_COLORS = ['black', 'tan']
def hex_cell(i, j, value):
  push_state()
  (x, y) = position(i, j)
  turtle.setposition(turtle.xcor() + x, turtle.ycor() + y)
  draw_hex(HEX_COLORS[value])
  pop_state()

def draw_hex_cells(xorigin, yorigin, cells):
  turtle.tracer(0, 0)
  turtle.hideturtle()
  turtle.speed(0)
  push_state()
  turtle.penup()
  turtle.setposition(xorigin, yorigin)
  turtle.pencolor('#8080ff')
  for i in range(len(cells)):
    for j in range(len(cells[i])):
      if cells[i][j] is not None:
        hex_cell(i, j, cells[i][j])
  pop_state()
  turtle.update()
