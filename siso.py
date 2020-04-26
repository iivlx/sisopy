from tkinter import Tk, ttk, TclError, StringVar
from tkinter import PhotoImage, Canvas
from tkinter import (Toplevel, Menu, Text)
from tkinter import filedialog
from tkinter.ttk import (Style, Frame, Label, PanedWindow, Button, Combobox, Entry, Separator)
from tkinter.constants import LEFT, SEL, INSERT, DISABLED, NORMAL, END, CENTER, YES, ACTIVE, SUNKEN, RIGHT, CURRENT
from math import floor

from icon import loadIcon, IIVLXICO
from data import *
from tile import Tile

import time
import random

class Siso(Frame):
    ''' Main window of the application    
    '''
    WINDOW_TITLE = "siso - iivlx"
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 260
    WINDOW_WIDTH_MIN = 500
    WINDOW_HEIGHT_MIN = 250
    WINDOW_WIDTH_OFFSET = 100
    WINDOW_HEIGHT_OFFSET = 100
    WINDOW_Y_MIN = 50
    WINDOW_RESIZABLE = (True, True)
    
    def __init__(self, master, **kw):
        Frame.__init__(self, master, **kw)
        self.style = Style()
        self.configure()
        # window title and icon
        loadIcon(self.master, self.master, IIVLXICO)
        self.master.title(self.WINDOW_TITLE) 
        # window geometry
        self.master.resizable(*self.WINDOW_RESIZABLE)
        x = self.master.winfo_pointerx() - self.WINDOW_WIDTH_OFFSET
        y = self.master.winfo_pointery() - self.WINDOW_HEIGHT_OFFSET
        y = y if y > self.WINDOW_Y_MIN else self.WINDOW_Y_MIN
        geometry = '{0:d}x{0:d}+{2:d}+{3:d}'.format(self.WINDOW_WIDTH, self.WINDOW_HEIGHT, x, y)
        self.master.geometry(geometry)
        self.master.minsize(self.WINDOW_WIDTH_MIN,
                            self.WINDOW_HEIGHT_MIN)
        # master window grid
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        # place the window
        self.grid(row=0, column=0, sticky='news')
        # this window grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)
        # create tilemap
        self.tiles = []
        self.loadTiles(TILEMAPFILE)
        #self.createMenubar()
        self.createCanvas()
        #self.createContextMenu()
        self.draw()
        self.setBinds()
                
        
    def createTiles(self, rows, columns):
        ''' Create a new blank tilemap '''
        color = '#009900'
        tiles = []
        for r in range(rows):
            row = []
            for c in range(columns):
                newtile = Tile()
                newtile.color = color
                newtile.r = r
                newtile.c = c
                row.append(Tile([color,0,0,0,0]))
            tiles.append(row)
        self.tiles = tiles
        
    def loadTiles(self, file):
        ''' load tilemap form a file '''
        tiles = []
        with open(file) as f:
            r = 0
            for line in f:
                    c = 0
                    row = []
                    # split the data in tiles for the row
                    rowdata = line.replace('\n', '')
                    tiledata = rowdata.split(', ')
                    # create each tile
                    for tile in tiledata:
                        d = tile.strip('()').split(',')
                        newtile = Tile()
                        newtile.color = '#'+d[0]
                        newtile.ht = int(d[1])
                        newtile.hr = int(d[2])
                        newtile.hl = int(d[3])
                        newtile.hb = int(d[4])
                        newtile.r = r
                        newtile.c = c
                        row.append(newtile)
                        c += 1
                    # add the row to the tile array
                    tiles.append(row)
                    r += 1
            self.tiles = tiles

        
    
    def createCanvas(self):
        ''' Create the main canvas '''
        self.canvas = Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background=CANVAS_BG)
        self.canvas.grid(row=0,column=0)
        self.canvas.gh = GH
        self.canvas.gw = GW
        self.canvas.gs = GS
        self.canvas.offsetx = self.WINDOW_WIDTH /2
        self.canvas.offsety = GH * 3
        self.canvas.coordinates = False
        
    def setBinds(self):
        ''' Set binds for this window '''
        self.canvas.bind_all('<Key>', self.handleKeyPress)
        self.canvas.bind_all('<MouseWheel>', self.handleMouseWheel)
        
    def redraw(self):
        ''' Clear the canvas and redraw everything'''
        self.canvas.delete("all")
        self.draw()
        
    def draw(self):
        ''' Draw '''
        self.drawTiles()
        
        
    def drawTiles(self):
        ''' Draw the tilemap '''
        for r, row in enumerate(self.tiles):
            for c, tile in enumerate(row):
                self.drawTile(r, c, tile)

    def getTileFromEvent(self, event):
        ''' Get a tile from a click event '''
        # Find the tile clicked
        clicked = event.widget.find_withtag('current')[0]
        tags = self.canvas.gettags(clicked)
        gridtag = tags[0]
        # r,c of tile clicked
        r,c = gridtag[1:].split('x')
        tile = self.tiles[int(r)][int(c)]  
        return tile
        
    def handleMouseWheel(self, event):
        if event.delta > 0:
            self.canvas.gh *= 2
            self.canvas.gs *= 2
            self.canvas.gw = self.canvas.gh * 2
        elif event.delta < 0:
            self.canvas.gh /= 2
            self.canvas.gs /= 2
            self.canvas.gw = self.canvas.gh * 2
        self.redraw()
            
    def handleKeyPress(self, event):
        ''' Handle a keyboard event '''
        if event.keycode == 87: # w
            self.increaseTileHT(self.selected)
        elif event.keycode == 65: # a
            self.increaseTileHL(self.selected)
        elif event.keycode == 83: # s
            self.increaseTileHB(self.selected)
        elif event.keycode == 68: # d
            self.increaseTileHR(self.selected)
        elif event.keycode == 37: # left
            self.canvas.offsetx += 30
        elif event.keycode == 38: # up
            self.canvas.offsety += 30
        elif event.keycode == 39: # right
            self.canvas.offsetx -= 30
        elif event.keycode == 40: # down
            self.canvas.offsety -= 30
        elif event.keycode == 67: # c
            self.canvas.coordinates = False if self.canvas.coordinates else True # toggle coordinates
        else:
            print(event.keycode)
            return
        self.redraw()
        
    def increaseTileHT(self, tile, amount=5):
        ''' Increase the top corner of one tile and surrounding tiles '''
        if tile.r > 0:
            self.tiles[tile.r-1][tile.c].hl += amount
        if tile.c > 0:
            self.tiles[tile.r][tile.c-1].hr += amount
        if tile.c > 0 and tile.r > 0:
            self.tiles[tile.r-1][tile.c-1].hb += amount        
        tile.ht += amount
    
    def increaseTileHR(self, tile, amount=5):
        ''' Increase the right corner of one tile and surrounding tiles '''
        if tile.r > 0:
            try: # tile previous row
                self.tiles[tile.r-1][tile.c].hb += amount
            except IndexError:
                pass
                
            try: # tile previous row next column
                self.tiles[tile.r-1][tile.c+1].hl += amount
            except IndexError:
                pass
        try: # next tile in row
            self.tiles[tile.r][tile.c+1].ht += amount
        except IndexError:
            pass 
        tile.hr += amount
        
    def increaseTileHL(self, tile, amount=5):
        ''' Increase the left corner of one tile and surrounding tiles '''
        try:
            self.tiles[tile.r+1][tile.c].ht += amount
        except IndexError:
            pass    
        if tile.c > 0:
            try:
                self.tiles[tile.r][tile.c-1].hb += amount
            except IndexError:
                pass    
            try:
                self.tiles[tile.r+1][tile.c-1].hr += amount
            except IndexError:
                pass    
            
        tile.hl += amount

    def increaseTileHB(self, tile, amount=5):
        ''' Increase the bottom corner of one tile and surrounding tiles '''
        try: # 
            self.tiles[tile.r+1][tile.c].hr += amount
        except IndexError:
            pass    
        try:
            self.tiles[tile.r][tile.c+1].hl += amount
        except IndexError:
            pass    
        try:
            self.tiles[tile.r+1][tile.c+1].ht += amount
        except IndexError:
            pass    
        tile.hb += amount
        
        
    def tileClick(self, event):
        ''' click on a tile '''
        tile = self.getTileFromEvent(event)
        self.selected = tile
        self.redraw()
        
    def tileRightClick(self, event):
        ''' right click on a tile '''
        tile = self.getTileFromEvent(event)
        self.increaseTileHeight(tile)
    
    def increaseTileHeight(self, tile):
        ''' Increase the height of all the corners of a tile and the surrounding tiles affected corners '''
        self.increaseTileHB(self.tiles[tile.r][tile.c], 10)
        self.increaseTileHR(self.tiles[tile.r][tile.c], 10)
        self.increaseTileHL(self.tiles[tile.r][tile.c], 10)
        self.increaseTileHT(self.tiles[tile.r][tile.c], 10)
        self.redraw()
                
    def drawCircleAtRC(self, r, c, offsetx=350, offsety=80):
        ''' Draw a circle at a tile coordinates '''
        x = (c-r)*(GW/2) + offsetx
        y = (c+r)*(GH/2) + offsety
        
        y += GH/2
        size = GH/4
        
        self.canvas.create_oval(x-size,y-size,x+size,y+size, fill=e[2])
        
    def drawTile(self, r, c, tile):
        ''' Draw a tile '''
        gw = self.canvas.gw
        gh = self.canvas.gh
        gs = self.canvas.gs
        
        offsetx = self.canvas.offsetx * self.canvas.gs
        offsety = self.canvas.offsety * self.canvas.gs
        
        ht = tile.ht * gs
        hr = tile.hr * gs
        hl = tile.hl * gs
        hb = tile.hb * gs
        cl = tile.color
        
        
        x = (c-r)*(gw/2) + offsetx # x increases for every row, decreases for every column
        y = (c+r)*(gh/2) + offsety # y decreases for every column and row
        
        self.canvas.create_polygon(
            x, y - ht,                            # top
            x+(gw/2), y+(gh/2) - hr,              # right
            x, y+(gh) - hb,                       # bottom
            x-(gw/2), y+(gh/2) - hl,              # left
            fill=cl,
            activefill='white',
            outline='black',
            tags=f't{r}x{c}',
            )

        self.canvas.tag_bind(f't{r}x{c}', '<Button-1>', self.tileClick)
        self.canvas.tag_bind(f't{r}x{c}', '<Button-3>', self.tileRightClick)
        
        if self.canvas.coordinates:
            self.canvas.create_text(x+10, y+10, text=f'{r}, {c}')


    
if __name__ == '__main__':
    import main
    
    
    
    
    
    