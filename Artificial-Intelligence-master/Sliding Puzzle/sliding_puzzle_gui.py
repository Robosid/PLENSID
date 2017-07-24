
#
# a Tk GUI
#

'''
  http://effbot.org/tkinterbook/canvas.htm

  Last modified 2015-03-07 by n9840371@qut.edu.au (Sid Mahapatra)
'''

# For compatibility with Python 2.7
# A future statement is a directive to the compiler that a particular module 
# should be compiled using syntax or semantics that will be available in a 
# specified future release of Python.
# The future statement is intended to ease migration to future versions of 
# Python that introduce incompatible changes to the language. It allows use 
# of the new features on a per-module basis before the release in which the 
# feature becomes standard.
from __future__ import print_function
from __future__ import division


import threading
import sys
import time
import argparse

#from sliding_puzzle import Sliding_puzzle

if sys.version_info[0] == 2:
  from Tkinter import *
else:
  from tkinter import *

import search
from sliding_puzzle import Sliding_puzzle


# Dimension of the grid of the sliding puzzle
numberOfRows = 3 #4
numberOfColumns = 4 # 6
numberOfScrambleSteps = 5



DEFAULTS = {
  # colours: background, foreground, highlight
  'bg': 'white', 'fg': 'black', 'hl': 'yellow',
  # fonts
  'font': 'Helvetica',
  # puzzle dimensions
  'm': numberOfColumns, 'n': numberOfRows,
  # size of components
  'padx': 16, 'pady': 16, 'frame': 8, 'border': 4,
  # sliding animation
  'steps': 2, 'delay': 5,
}

class App(Frame):

  def __init__(self):
    self.moving = None

    # arguments
    args = self.args()
    self.m = args.m # width, number of columns
    self.n = args.n # height, number of rows
    
    t = args.t
    if len(t) == 0: t = list(range(self.m * self.n - 1, 0, -1))
    if len(t) < self.m * self.n: t += [0]
    self.target_args = (t if len(args.t) > 0 else None)

    self.board = list(range(1,self.m*self.n))+[0] # range(self.m * self.n-1,-1,-1)

    self.fg = args.fg
    self.bg = args.bg
    self.hl = args.hl
    self.font = args.font
    self.padx = args.padx
    self.pady = args.pady
    self.frame = args.frame
    self.border = args.border
    self.steps = args.steps # animation: number of steps when sliding a tile
    self.delay = args.delay # animation: delay for sliding effect
    self.init()

  def args(self):
    arg = argparse.ArgumentParser(description='Sliding Puzzle.')
    arg.add_argument('-fg', '--foreground', dest='fg', default=DEFAULTS['fg'], help='foreground colour (default: {d})'.format(d=DEFAULTS['fg']))
    arg.add_argument('-bg', '--background', dest='bg', default=DEFAULTS['bg'], help='background colour (default: {d})'.format(d=DEFAULTS['bg']))
    arg.add_argument('-hl', '--highlight', dest='hl', default=DEFAULTS['hl'], help='highlight colour (default: {d})'.format(d=DEFAULTS['hl']))
    arg.add_argument('-fn', '--font', dest='font', default=DEFAULTS['font'], help='font (default: {d})'.format(d=DEFAULTS['font']))
    arg.add_argument('-f', '--frame', dest='frame', type=int, default=DEFAULTS['frame'], help='puzzle frame width (default: {d})'.format(d=DEFAULTS['frame']))
    arg.add_argument('-b', '--border', dest='border', type=int, default=DEFAULTS['border'], help='tile highlight width (default: {d})'.format(d=DEFAULTS['border']))
    arg.add_argument('-px', '--padx', dest='padx', type=int, default=DEFAULTS['padx'], help='puzzle pad x (default: {d})'.format(d=DEFAULTS['padx']))
    arg.add_argument('-py', '--pady', dest='pady', type=int, default=DEFAULTS['pady'], help='puzzle pad y (default: {d})'.format(d=DEFAULTS['pady']))
    arg.add_argument('-s', '--steps', dest='steps', type=int, default=DEFAULTS['steps'], help='number of steps in slide (default: {d})'.format(d=DEFAULTS['steps']))
    arg.add_argument('-d', '--delay', dest='delay', type=int, default=DEFAULTS['delay'], help='ms delay between steps (default: {d})'.format(d=DEFAULTS['delay']))
    arg.add_argument(metavar='M', dest='m', type=int, nargs='?', default=DEFAULTS['m'], help='puzzle width (default: {d})'.format(d=DEFAULTS['m']))
    arg.add_argument(metavar='N', dest='n', type=int, nargs='?', default=DEFAULTS['n'], help='puzzle height (default: {d})'.format(d=DEFAULTS['n']))
    arg.add_argument(metavar='T', dest='t', type=int, nargs='*', help='target configuration')
    return arg.parse_args()


  def init(self, master=None):
    Frame.__init__(self, master)
    # make the application resizable
    top = self.winfo_toplevel()
    top.rowconfigure(0, weight=1)
    top.columnconfigure(0, weight=1)
    self.grid(sticky=N+S+E+W)
    # now create the UI elements
    self.start()


  def start(self):
    self.master.title('CAB320 - Week 03 - Sliding Puzzle')

    # control buttons
    buttons = Frame(self)
    solve_button = Button(buttons, text="Solve", command=self.solve)
    solve_button.pack(side=LEFT, padx=10)
    self.solve_button = solve_button
    scramble_button = Button(buttons, text="Scramble", command=self.scramble)
    scramble_button.pack(side=LEFT, padx=10)
    reset_board_button = Button(buttons, text="Reset Board", command=self.reset_board)
    reset_board_button.pack(side=LEFT, padx=10)
    quit_button = Button(buttons, text="Quit", command=self.quit)
    quit_button.pack(side=RIGHT, padx=10)

    # main display aread
    canvas = Canvas(self, width=640, height=480, background='light grey')

    buttons.grid(column=0, row=0, sticky=N+E+W)
    canvas.grid(column=0, row=1, sticky=N+S+E+W)

    self.columnconfigure(0, weight=1)
    self.rowconfigure(1, weight=1)

    # interaction, click on the canvas
    canvas.bind('<1>', self.click)
    canvas.bind('<Configure>', self.draw)
    self.canvas = canvas
    
  def reset_board(self):
    self.board = list(range(1,self.m*self.n))+[0] # 
    self.draw()

  # Generator function of the positions adjacent to <p>
  def adjacent(self, p):
    (m, n) = (self.m, self.n)
    (p0, p1) = divmod(p, m)
    if p0 > 0: yield p - m
    if p0 + 1 < n: yield p + m
    if p1 > 0: yield p - 1
    if p1 + 1 < m: yield p + 1

  def draw(self, event=None):
    # clear the canvas
    self.canvas.delete(ALL)

    # get the dimensions of the canvas
    cw = self.canvas.winfo_width()
    ch = self.canvas.winfo_height()
    
    # compute the size of a tile
    (x0, y0, frame, border) = (self.padx, self.pady, self.frame, self.border)
    tile = min((cw - 2 * (x0 + frame) - (self.m + 1) * border) // self.m, (ch - 2 * (y0 + frame) - (self.n + 1) * border) // self.n)
    x0 = (cw - 2 * frame - self.m * (border + tile) - border) // 2
    y0 = (ch - 2 * frame - self.n * (border + tile) - border) // 2
    font = [self.font, tile // 2, 'bold']

    # draw the frame
    (fw, fh, fb) = (self.m * (tile + border) + border, self.n * (tile + border) + border, frame // 2)
    #self.canvas.create_rectangle(x0 + fb, y0 + fb, x0 + fw + 3 * fb, y0 + fh + 3 * fb, outline=self.fg, width=frame)
    self.canvas.create_rectangle(x0 , y0 , x0 + fw + 3 * fb, y0 + fh + 3 * fb, outline=self.fg, width=frame)


    # draw the tiles
    # x,i,m horizontal.  y,j,n  vertical
    for i in range(self.m):
      for j in range(self.n):
##        (x, y) = (x0 + i * (tile + border) + border, y0 + j * (tile + border) + border)
        (x, y) = (x0 + i * (tile + border) + 2*border, y0 + j * (tile + border) + 2*border)
        p = j * self.m + i
        # assert len(self.board)==self.m*self.n
        t = self.board[p]
        # the blank and the moving tile (if any) are drawn later
        if t == 0 or p == self.moving: continue
        tag = 'pos=' + str(p)
        self.canvas.create_rectangle(x + 1, y + 1, x + tile - 1, y + tile - 1, outline=self.fg, width=2, tags=tag)
        self.canvas.create_text(x + tile // 2, y + tile // 2, text=t, font=font, tags=tag)

    # draw any moving tile
    if self.moving is not None:
      t = self.board[self.moving]
      (i, j) = divmod(self.moving, self.m)
      (x, y) = (x0 + j * (tile + border) + 2*border, y0 + i * (tile + border) + 2*border)
      (xo, yo) = (tile * self.offset[0] * self.offset[2] // self.steps, tile * self.offset[1] * self.offset[2] // self.steps)
      self.canvas.create_rectangle(x + xo + 1, y + yo + 1, x + tile + xo - 1, y + tile + yo - 1, outline=self.fg, width=2)
      self.canvas.create_text(x + tile // 2 + xo, y + tile // 2 + yo, text=t, font=font)


  def move(self, p):
    b = self.board.index(0) 
    if b not in self.adjacent(p):
      print ( 'Warning: p = {0} and b = {1} not adjacent in move()'.format(p,b) )
      return
    self.moving = p
    if b == p + self.m: (x, y) = (0, 1) # relative motion
    elif b == p - self.m: (x, y) = (0, -1)
    elif b == p + 1: (x, y) = (1, 0)
    elif b == p - 1: (x, y) = (-1, 0)
    self.offset = list((x, y)) + [0]  # triplet x,y,step
##    for self.offset[2] in range(self.steps):
##      self.draw()
##      time.sleep(0.02)
##    self.board[b], self.board[self.moving] = self.board[self.moving] , self.board[b] 
##    self.moving = None
##    self.draw()
    self.slide()


  # move the tile at position index p
  def click_move(self, p):
    assert 0<=p<self.n*self.m
    b = self.board.index(0) 
    if b not in self.adjacent(p):
      print( 'Warning: p = {0} and b = {1} not adjacent in move()'.format(p,b) )
      return
    self.moving = p
    if b == p + self.m: (x, y) = (0, 1) # relative motion
    elif b == p - self.m: (x, y) = (0, -1)
    elif b == p + 1: (x, y) = (1, 0)
    elif b == p - 1: (x, y) = (-1, 0)
    self.offset = list((x, y)) + [0]  # triplet x,y,step
    # set a timer to update the offset
    # self.after(self.delay, self.slide)
    # time.sleep(0.1)
    self.slide() # non  blocking!
    


  def slide(self):
    assert self.moving is not None
##    print 'in slide, moving is ', self.moving
##    print 'in slide, offset ', self.offset , ' < ', self.steps
    if self.offset[2] < self.steps:
      self.offset[2] += 1
      self.after(self.delay, self.slide)
      #time.sleep(0.2)
      #self.slide()
    else:
      # move finihsed
      # reflect change in self.board
      b = self.board.index(0)
      self.board[b], self.board[self.moving] = self.board[self.moving] , self.board[b] 
      self.moving = None
    self.draw()


  def click(self, event):
    '''
    Handler for click on tile
    '''
    w = event.widget.find_withtag(CURRENT)
    if not w: return
    for tag in event.widget.gettags(w):
      if tag.startswith('pos='):
        p = int(tag[4:])
        #if self.start_time is None: self.start_time = time.time()
        self.click_move(p)
    self.draw()

  def scramble(self):
    sp = Sliding_puzzle(self.n, # number of rows
                        self.m) # number of columns
    # need a list type for swapping elements
    self.board = list(sp.random_state(self.board, n=numberOfScrambleSteps))    
    self.draw()


  from search import breadth_first_tree_search, Node  
  def solve(self):
    self.solve_button.configure(text='Stop', command=self.stop)
    self.solverThread = threading.Thread(target=self.solve_fn)
    self.solverThread.daemon = True
    self.solverThread.start()
    
  def solve_fn(self):
    # make a copy of the puzzle to determine the moves
    sp = Sliding_puzzle(self.n, # number of rows
                        self.m, # number of columns
                        goal = list(range(1, self.m*self.n))+[0] ,
                        initial = self.board)
    # sol_ts : goal leaf node of the solution tree search
    print ('** Starting the breadth_first_tree_search **')
    t0 = time.time()
    sol_ts = search.breadth_first_tree_search(sp)
##    sol_ts = breadth_first_search_v0(sp)
    t1 = time.time()
    sp.print_solution(sol_ts)
    print ("Solver took ",t1-t0, ' seconds')

    # The actions are 'U','D','L' and 'R'  (move the blank tile up, down, left  right)
    # b = self.board.index(0) # position index of the blank tile
    # p = b + offsetDict[cmd]  is the index of the tile to move 
    offsetDict = {'U':-self.m, 'D':self.m, 'L':-1 , 'R':1} 
    for node in sol_ts.path():
      if node.action: # root action is None and should be skipped
        assert node.action in ['U','D','L','R']
        p = self.board.index(0) + offsetDict[node.action]
        self.move(p)
        while self.moving is not None:
          time.sleep(0.1)
    self.solve_button.configure(text='Solve', command=self.solve)
##        print 'in solve, self.moving is ', self.moving 
##        while self.moving is not None:
##          print '.'

  def stop(self):
    self.solverThread._Thread__stop()
    self.solve_button.configure(text='Solve', command=self.solve)
        
          
if __name__ == '__main__':
  # create the UI
  app = App()
  app.draw()
  app.mainloop()


# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + 
#                              CODE CEMETARY
# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + 




##  def slide(self):
##    assert self.moving is not None
##    for self.offset[2] in range(self.steps):
##      time.sleep(0.1)
##      self.draw()
##    b = self.board.index(0)
##    self.board[b], self.board[self.moving] = self.board[self.moving] , self.board[b] 
##    self.moving = None

##    
##
##
####    p = self..copy()
##    try:
##      self.count = 0
##      self.start_time = time.time()
##      self.solve_button.configure(text='Stop', command=self.stop)
##      self.automate(p.solve())
##    except Impossible:
##      self.message.set("Impossible Target")
##      self.stop()
##
##  def stop(self):
##    self.moves = []
##    self.solve_button.configure(text='Solve', command=self.solve)
