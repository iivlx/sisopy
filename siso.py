from tkinter import Tk, ttk, TclError, StringVar
from tkinter import PhotoImage, Canvas
from tkinter import (Toplevel, Menu, Text)
from tkinter import filedialog, colorchooser
from tkinter.ttk import (Style, Frame, Label, PanedWindow, Button, Combobox, Entry, Separator)
from tkinter.constants import LEFT, SEL, INSERT, DISABLED, NORMAL, END, CENTER, YES, ACTIVE, SUNKEN, RIGHT, CURRENT
from math import floor
from PIL import ImageTk
from PIL import Image

from os import listdir
from os.path import isfile, join
from icon import loadIcon, IIVLXICO
from data import *
from tile import Tile

import time
import random
import math

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
        self.loadTextures(TEXTUREDIRECTORY)
        self.loadTiles(TILEMAPFILE)
        self.createMenubar()
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
                row.append(newtile)
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

    def loadTextures(self, directory):
        ''' load all textures from a directory'''
        textures = {}
        for file in listdir(directory):
            if not isfile(join(directory, file)): # skip if directory
               continue
            with open(f"{directory}/{file}") as f:
                texture = PhotoImage(file=f"{directory}/{file}")
                textures[file] = texture
        self.textures = textures


    def newTilemapDialog(self):
        self.createTiles(20, 20)
        self.redraw()
        
    def tileColorDialog(self):
        ''' Set the color to change tiles to '''
        self.canvas.tilecolor = colorchooser.askcolor()[1]
        self.canvas.action = 'color'
        
    def tileActionRaise(self):
        self.canvas.action = 'raise'
    
    def tileActionLower(self):
        self.canvas.action = 'lower'
    
    def createCanvas(self):
        ''' Create the main canvas '''
        self.canvas = Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background=CANVAS_BG)
        self.canvas.grid(row=0,column=0)
        self.canvas.width = CANVAS_WIDTH
        self.canvas.height = CANVAS_HEIGHT
        self.canvas.gh = GH
        self.canvas.gw = GW
        self.canvas.gs = GS
        self.canvas.offsetx = self.WINDOW_WIDTH /2
        self.canvas.offsety = GH * 3
        self.canvas.coordinates = False
        self.canvas.tilecolor = '#ff9900'
        self.canvas.action = 'raise'

    
    def createMenubar(self):
        ''' Create the Menubar '''
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)
        # add submenus
        self.menubar.add_cascade(label='File', menu=self.createMenubarFile())
        self.menubar.add_cascade(label='Edit', menu=None)
        self.menubar.add_cascade(label='Action', menu=self.createMenubarAction())
        self.menubar.add_cascade(label='View', menu=self.createMenubarView())
        self.menubar.add_cascade(label='Help', menu=None)
        
    def createMenubarFile(self):
        ''' Create the File submenu '''
        self.menubar_file = Menu(self.menubar, tearoff=0)
        self.menubar_file.add_command(label='New', command=self.newTilemapDialog)
        self.menubar_file.add_command(label='Load')
        self.menubar_file.add_command(label='Save')
        self.menubar_file.add_separator()
        self.menubar_file.add_command(label='Exit', command=self.quit)
        return self.menubar_file      
      
    def createMenubarAction(self):
        ''' Create the Action submenu '''
        self.menubar_action = Menu(self.menubar, tearoff=0)
        self.menubar_action.add_command(label='Raise', command=self.tileActionRaise)
        self.menubar_action.add_command(label='Lower', command=self.tileActionLower)
        self.menubar_action.add_command(label='Color', command=self.tileColorDialog)
        return self.menubar_action
    
    def createMenubarView(self):
        ''' Create the View submenu '''
        self.menubar_action = Menu(self.menubar, tearoff=0)
        self.menubar_action.add_command(label='Reset', command=self.viewReset)
        return self.menubar_action
    
    def viewReset(self):
        ''' Reset the viewbox '''
        self.canvas.offsetx = 0
        self.canvas.offsety = 0
        self.redraw()
        
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
        
#         self.canvas.create_line(0,self.canvas.width/2, self.canvas.height, self.canvas.width/2)
#         self.canvas.create_line(self.canvas.height/2, 0, self.canvas.height/2, self.canvas.width)
        
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
        ''' When the mousewheel is scrolled 
        Zoom in/out and adjust the position of the camera
        '''
        zscale = 0.1
        if event.delta > 0:
            zoom = math.exp(1*zscale)            
        elif event.delta < 0:
            zoom = math.exp(-1*zscale)
            
        mousex = event.x - self.canvas.offsetx # mouse x position
        mousey = event.y - self.canvas.offsety # mouse y position
#         mousex = (self.canvas.width/2) - self.canvas.offsetx # center of canvas
#         mousey = (self.canvas.height/2) - self.canvas.offsety # center of canvas
        
        
        self.canvas.offsetx += mousex/(self.canvas.gs*zoom) - mousex/self.canvas.gs
        self.canvas.offsety += mousey/(self.canvas.gs*zoom) - mousey/self.canvas.gs

            
        self.canvas.gs *= zoom # scale
        self.canvas.gh *= zoom
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
        
    def setTileColor(self, tile):
        ''' Change the color of a tile '''
        self.tiles[tile.r][tile.c].color = self.canvas.tilecolor
        self.redraw()
        
    def getTileRight(self, tile):
        if tile.r == 0: # no tile
            return None
        try:
            return self.tiles[tile.r-1][tile.c+1]
        except IndexError:
            return None
        
    def getTileLeft(self, tile):
        if tile.c == 0: # no tile
            return None
        try:
            return self.tiles[tile.r+1][tile.c-1]
        except IndexError:
            return None
        
    def getTileTop(self, tile):
        if tile.c == 0 or tile.r == 0: # no tile
            return None
        try:
            return self.tiles[tile.r-1][tile.c-1]
        except IndexError:
            return None
        
    def getTileBottom(self, tile):
        try:
            return self.tiles[tile.r+1][tile.c+1]
        except IndexError:
            return None
        
    def getTileTopRight(self, tile):
        if tile.r == 0: # no tile
            return None
        try:
            return self.tiles[tile.r-1][tile.c]
        except IndexError:
            return None
                
    def getTileTopLeft(self, tile):
        if tile.c == 0: # no tile
            return None
        try:
            return self.tiles[tile.r][tile.c-1]
        except IndexError:
            return None
        
    def getTileBottomRight(self, tile):
        try:
            return self.tiles[tile.r][tile.c+1]
        except IndexError:
            return None
                
    def getTileBottomLeft(self, tile):
        try:
            return self.tiles[tile.r+1][tile.c]
        except IndexError:
            return None      
        
    def increaseTileHT(self, tile, amount=16):
        ''' Increase the top corner of one tile and surrounding tiles '''
        max = tile.ht - amount
        top = self.getTileTop(tile)
        topright = self.getTileTopRight(tile)
        topleft = self.getTileTopLeft(tile)
        # check tiles
        if tile.hl <= max or tile.hr <= max:
            return False
        if top:
            if top.hl <= max or top.hr <= max:
                return False
        if topright:
            if topright.ht <= max or topright.hb <= max:
                return False
        if topleft:
            if topleft.ht <= max or topleft.hb <= max:
                return False
        # increase vertices
        if top:
            top.hb += amount       
        if topright:
            topright.hl += amount
        if topleft:
            topleft.hr += amount
            
             
        tile.ht += amount
    
    def increaseTileHR(self, tile, amount=16):
        ''' Increase the right corner of one tile and surrounding tiles '''
        max = tile.hr - amount
        topright = self.getTileTopRight(tile)
        bottomright = self.getTileBottomRight(tile)
        right = self.getTileRight(tile)
        # check tiles
        if tile.ht <= max or tile.hb <= max:
            return False
        if topright:
            if topright.hl <= max or topright.hr <= max:
                return False
        if right:
            if right.ht <= max or right.hb <= max:
                return False
        if bottomright:
            if bottomright.hl <= max or bottomright.hr <= max:
                return False
        # increase vertices
        if topright:
            topright.hb += amount
        if bottomright:
            bottomright.ht += amount
        if right:
            right.hl += amount
        tile.hr += amount
        
    def increaseTileHL(self, tile, amount=16):
        ''' Increase the left corner of one tile and surrounding tiles '''
        max = tile.hl - amount
        topleft = self.getTileTopLeft(tile)
        left = self.getTileLeft(tile)
        bottomleft = self.getTileBottomLeft(tile)
        # check tiles
        if tile.ht <= max or tile.hb <= max:
            return False
        if topleft:
            if topleft.hl <= max or topleft.hr <= max:
                return False
        if left:
            if left.ht <= max or left.hb <= max:
                return False
        if bottomleft:
            if bottomleft.hl <= max or bottomleft.hr <= max:
                return False
        # increase vertices
        if topleft:
            self.getTileTopLeft(tile).hb += amount
        if left:
            self.getTileLeft(tile).hr += amount
        if bottomleft:
            self.getTileBottomLeft(tile).ht += amount
        tile.hl += amount

    def increaseTileHB(self, tile, amount=16):
        ''' Increase the bottom corner of one tile and surrounding tiles '''
        max = tile.hb - amount
        bottomright = self.getTileBottomRight(tile)
        bottomleft = self.getTileBottomLeft(tile)
        bottom = self.getTileBottom(tile)
        # check tiles
        if tile.hl <= max or tile.hr <= max:
            return False
        if bottomleft:
            if bottomleft.ht <= max or bottomleft.hb <= max:
                    return False
        if bottomright:
            if bottomright.ht <= max or bottomright.hb <= max:
                return False
        if bottom:
            if bottom.hl <= max or bottom.ht <= max:
                return False
        # increase vertices
        if bottom:
            bottom.ht += amount
        if bottomright:
            bottomright.hl += amount
        if bottomleft:
            bottomleft.hr += amount
        tile.hb += amount
        
        
    def tileClick(self, event):
        ''' click on a tile '''
        tile = self.getTileFromEvent(event)
        self.selected = tile
        self.redraw()
        
    def tileRightClick(self, event):
        ''' right click on a tile '''
        tile = self.getTileFromEvent(event)
        #print(self.canvas.action)
        if self.canvas.action == 'lower':
            self.decreaseTileHeight(tile)
        elif self.canvas.action == 'raise':
            self.increaseTileHeight(tile)
        elif self.canvas.action == 'color':
            self.setTileColor(tile)
    
    def increaseTileHeight(self, tile, amount=16):
        ''' Increase the height of all the corners of a tile and the surrounding tiles affected corners '''
        self.increaseTileHB(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHR(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHL(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHT(self.tiles[tile.r][tile.c], amount)
        self.redraw()

    def decreaseTileHeight(self, tile, amount=10):
        ''' Decrease the height of all the corners of a tile and the surrounding tiles affected corners '''
        amount *= -1
        self.increaseTileHB(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHR(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHL(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHT(self.tiles[tile.r][tile.c], amount)
        self.redraw()
                
    def drawCircleAtRC(self, r, c, offsetx=350, offsety=80):
        ''' Draw a circle at a tile coordinates '''
        x = (c-r)*(GW/2) + offsetx
        y = (c+r)*(GH/2) + offsety
        
        y += GH/2
        size = GH/4
        
        self.canvas.create_oval(x-size,y-size,x+size,y+size, fill='red')
        
    def drawTile(self, r, c, tile):
        ''' Draw a tile '''
        gw = self.canvas.gw
        gh = self.canvas.gh
        gs = self.canvas.gs
        
        offsetx = self.canvas.offsetx
        offsety = self.canvas.offsety
        
        ht = tile.ht * gs
        hr = tile.hr * gs
        hl = tile.hl * gs
        hb = tile.hb * gs
        cl = tile.color
        
        x = (c-r)*(gw/2) + offsetx # x increases for every row, decreases for every column
        y = (c+r)*(gh/2) + offsety # y decreases for every column and row
        
        top = (x, y - ht)
        right = (x+(gw/2), y+(gh/2) - hr)
        bottom = (x, y+(gh) - hb)
        left = (x-(gw/2), y+(gh/2) - hl)
        
        flat = {'fill':'#99bc60'}
        slopel = {'fill':'#78a337'}
        sloper = {'fill':'#bce080'}
        config = {'outline':'#91b249', 'tags':f't{r}x{c}'}
        if ht == hr == hl == hb: # flat tile
            self.canvas.create_polygon(*top, *right, *bottom, *left, width=2, **flat, **config)
        elif hl == hb == hr and ht > hb: # slope top up
            self.canvas.create_polygon(*bottom, *right, *left, **flat, **config)
            self.canvas.create_polygon(*top, *right, *left, **slopel, **config)
        elif hl == hb == hr and ht < hb: # slope top down
            self.canvas.create_polygon(*bottom, *right, *left, **flat, **config)
            self.canvas.create_polygon(*top, *right, *left, **sloper, **config)
        elif hl == ht == hr and hb > ht: # slope bottom up
            self.canvas.create_polygon(*top,*right, *left, **flat, **config)
            self.canvas.create_polygon( *bottom, *right, *left, **sloper, **config)
        elif hl == ht == hr and hb < ht: # slope bottom down
            self.canvas.create_polygon(*top,*right, *left, **flat, **config)
            self.canvas.create_polygon( *bottom, *right, *left, **slopel, **config)
        elif ht == hb == hl and hr > hl: # slope right up
            self.canvas.create_polygon(*top,*bottom, *left, **flat, **config)
            self.canvas.create_polygon( *top, *bottom, *right, **slopel, **config)
        elif ht == hb == hl and hr < hl: # slope right down
            self.canvas.create_polygon(*top,*bottom, *left, **flat, **config)
            self.canvas.create_polygon( *top, *bottom, *right, **sloper, **config)
        elif ht == hb == hr and hl > hr: # slope left up
            self.canvas.create_polygon( *top, *bottom, *right, **flat, **config)
            self.canvas.create_polygon(*top,*bottom,*left, **sloper, **config)
        elif ht == hb == hr and hl < hr: # slope left down
            self.canvas.create_polygon(*top,*bottom, *left, **flat, **config)
            self.canvas.create_polygon( *top, *bottom, *right, **slopel, **config)
            
        elif ht == hr and hb == hl and ht > hb: # slope upright
            self.canvas.create_polygon(*top, *right, *bottom, *left, **slopel, **config)
        elif ht == hr and hb == hl and ht < hb: # slope downleft
            self.canvas.create_polygon(*top, *right, *bottom, *left, **sloper, **config)
        elif ht == hl and hb == hr and ht > hb: # slope upleft
            self.canvas.create_polygon(*top, *right, *bottom, *left, **sloper, **config)
        elif ht == hl and hb == hr and ht < hb: # slope downright
            self.canvas.create_polygon(*top, *right, *bottom, *left, **slopel, **config)
            
        elif hl == hr and hb < hl and ht > hl: # slope up
            self.canvas.create_polygon(*top, *right, *left, **slopel, **config)
            self.canvas.create_polygon(*bottom, *right, *left, **slopel, **config)
        elif hl == hr and hb > hl and ht < hl: # slope down
            self.canvas.create_polygon(*top, *right, *left, **sloper, **config)
            self.canvas.create_polygon(*bottom, *right, *left, **sloper, **config)
        elif ht == hb and hl < ht and hr > ht: # slope right
            self.canvas.create_polygon(*top, *bottom, *left, **slopel, **config)
            self.canvas.create_polygon(*top, *bottom, *right, **slopel, **config)
        elif ht == hb and hl > ht and hr < ht: # slope left
            self.canvas.create_polygon(*top, *bottom, *left, **sloper, **config)
            self.canvas.create_polygon(*top, *bottom, *right, **sloper, **config)
            
        elif ht == hb and hl < ht and hr < ht: # slope down left/right
            self.canvas.create_polygon(*top, *bottom, *left, **slopel, **config)
            self.canvas.create_polygon(*top, *bottom, *right, **sloper, **config)
        elif hl == hr and ht < hl and hb < hl: # slope down top/bottom
            self.canvas.create_polygon(*top, *left, *right, **sloper, **config)
            self.canvas.create_polygon(*bottom, *left, *right, **slopel, **config)
            
        else:
            print(ht, hr, hb, hl)
            self.canvas.create_polygon(*top, *right, *bottom, *left, **config)
            
        self.canvas.tag_bind(f't{r}x{c}', '<Button-1>', self.tileClick)
        self.canvas.tag_bind(f't{r}x{c}', '<Button-3>', self.tileRightClick)
        
        if self.canvas.coordinates:
            self.canvas.create_text(x+10, y+10, text=f'{r}, {c}')

    
if __name__ == '__main__':
    import main
    
    
    
    
    
    