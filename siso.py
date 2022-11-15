#!/usr/bin/env python3

''' siso Main Window '''

import time
import random
import math

from tkinter import Tk, ttk, TclError, StringVar, BooleanVar
from tkinter import PhotoImage, Canvas
from tkinter import (Toplevel, Menu, Text)
from tkinter import filedialog
from tkinter.ttk import (Style, Frame, Label, PanedWindow, Button, Combobox, Entry, Separator)
from tkinter.constants import LEFT, SEL, INSERT, DISABLED, NORMAL, END, CENTER, YES, ACTIVE, SUNKEN, RIGHT, CURRENT
from math import floor
from os import listdir
from os.path import isfile, join
from operator import ge, le

import pprint # sponge

from icon import loadIcon, IIVLXICO
from data import *
from tile import Tile
# from ui import ColorEditor # apparently this is missing...

class Siso(Frame):
    ''' Main window of the application    
    '''
    WINDOW_TITLE = "siso - iivlx"
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800
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
        geometry = '{0:d}x{1:d}+{2:d}+{3:d}'.format(self.WINDOW_WIDTH, self.WINDOW_HEIGHT, x, y)
        self.master.geometry(geometry)
        #self.master.minsize(self.WINDOW_WIDTH_MIN,
        #                    self.WINDOW_HEIGHT_MIN)
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
        #self.loadTextures(TEXTUREDIRECTORY)
        self.loadColors(COLORMAPFILE)
        self.loadTiles(TILEMAPFILE)
        self.createVariables()
        self.createMenubar()
        self.createCanvas()
        #self.createContextMenu()
        self.draw()
        self.setBinds()
                
        
    def createTiles(self, rows, columns):
        ''' Create a new blank tilemap '''
        tiles = []
        for r in range(rows):
            row = []
            for c in range(columns):
                newtile = Tile()
                newtile.color = 0
                newtile.ht = 0
                newtile.hr = 0
                newtile.hl = 0
                newtile.hb = 0
                newtile.r = r
                newtile.c = c
                row.append(newtile)
            tiles.append(row)
        self.tiles = tiles
        
    def loadColors(self, file):
        ''' load the color data from a file '''
        colors = []
        with open(file) as f:
            for line in f:
                rowdata = line.replace('\n', '')
                colordata = rowdata.split(', ')
                for color in colordata:
                    c = color.strip('()').split(',')
                    colors.append( (f'#{c[1]}', f'#{c[2]}', f'#{c[3]}', f'#{c[4]}') )
        self.colors = colors
        
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
                        newtile.color = int(d[0])
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
    
    def createVariables(self):
        ''' '''
        self.coordinates = BooleanVar()

    def newTilemapDialog(self):
        self.createTiles(4, 4)
        self.redraw()
        
    def tileColorDialog(self):
        ''' Set the color to change tiles to '''
        #self.coloreditor = ColorEditor(self) # show the color editor # -- which is apparently missing
        #self.canvas.action = 'color'
        
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
        self.canvas.baseheight = CANVAS_BASEHEIGHT
        self.canvas.offsetx = self.WINDOW_WIDTH /2
        self.canvas.offsety = GH * 3
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
        self.menubar_action.add_checkbutton(label='Coordinates', onvalue=1, offvalue=0, variable=self.coordinates, command=self.redraw)
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
        self.canvas.bind_all('<Button-1>', self.handleMouse1)
        self.canvas.bind_all('<B1-Motion>', self.handleMouse1Move)
        
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
    
    def handleMouse1(self, event):
        ''' When the left mouse is clicked '''
        
        self._mouseclickx = event.x
        self._mouseclicky = event.y
        
    def handleMouse1Move(self, event):
        ''' When the left mouse is clicked '''
        
        deltax = event.x - self._mouseclickx
        deltay = event.y - self._mouseclicky
        
        self._mouseclickx = event.x
        self._mouseclicky = event.y
        
        self.canvas.offsetx += deltax
        self.canvas.offsety += deltay
        self.redraw()
        
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
            if self.selected:
                self.increaseTileHT(self.selected)
        elif event.keycode == 65: # a
            if self.selected:
                self.increaseTileHL(self.selected)
        elif event.keycode == 83: # s
            if self.selected:
                self.increaseTileHB(self.selected)
        elif event.keycode == 68: # d
            if self.selected:
                self.increaseTileHR(self.selected)
        elif event.keycode == 37: # left
            self.canvas.offsetx += 30
        elif event.keycode == 38: # up
            self.canvas.offsety += 30
        elif event.keycode == 39: # right
            self.canvas.offsetx -= 30
        elif event.keycode == 40: # down
            self.canvas.offsety -= 30
        elif event.keycode == 86: # v
            if self.selected:
                print(self.selected.ht)
                print(self.selected.hr)
                print(self.selected.hb)
                print(self.selected.hl)
        elif event.keycode == 67: # c
            self.coordinates.set(False if self.coordinates.get() else True) # toggle coordinates
        elif event.keycode == 69: # e
            self.rotateTiles('clockwise')
        elif event.keycode == 81: # q
            self.rotateTiles('counterclockwise')
        elif event.keycode == 32: # space
            print('Tiles:')
            p = pprint.PrettyPrinter()
            p.pprint(self.tiles)
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
        
    def increaseTileHT(self, tile, amount=32):
        ''' Increase the top corner of one tile and surrounding tiles '''
        max = tile.ht - amount
        top = self.getTileTop(tile)
        topright = self.getTileTopRight(tile)
        topleft = self.getTileTopLeft(tile)
        # slope direction
        if amount > 0:
            op = le
        else:
            op = ge
        # check tiles
        if op(tile.hl, max) or op(tile.hr, max):
            return False
        if top:
            if op(top.hl, max) or op(top.hr, max):
                return False
        if topright:
            if op(topright.ht, max) or op(topright.hb, max):
                return False
        if topleft:
            if op(topleft.ht, max) or op(topleft.hb, max):
                return False
        # increase vertices
        if top:
            top.hb += amount       
        if topright:
            topright.hl += amount
        if topleft:
            topleft.hr += amount
            
             
        tile.ht += amount
    
    def increaseTileHR(self, tile, amount=32):
        ''' Increase the right corner of one tile and surrounding tiles '''
        max = tile.hr - amount
        topright = self.getTileTopRight(tile)
        bottomright = self.getTileBottomRight(tile)
        right = self.getTileRight(tile)
        # slope direction
        if amount > 0:
            op = le
        else:
            op = ge
        # check tiles
        if op(tile.ht, max) or op(tile.hb, max):
            return False
        if topright:
            if op(topright.hl, max) or op(topright.hr, max):
                return False
        if right:
            if op(right.ht, max) or op(right.hb, max):
                return False
        if bottomright:
            if op(bottomright.hl, max) or op(bottomright.hr, max):
                return False
        # increase vertices
        if topright:
            topright.hb += amount
        if bottomright:
            bottomright.ht += amount
        if right:
            right.hl += amount
        tile.hr += amount
        
    def increaseTileHL(self, tile, amount=32):
        ''' Increase the left corner of one tile and surrounding tiles '''
        max = tile.hl - amount
        topleft = self.getTileTopLeft(tile)
        left = self.getTileLeft(tile)
        bottomleft = self.getTileBottomLeft(tile)
        # slope direction
        if amount > 0:
            op = le
        else:
            op = ge
        # check tiles
        if op(tile.ht, max) or op(tile.hb, max):
            return False
        if topleft:
            if op(topleft.hl, max) or op(topleft.hr, max):
                return False
        if left:
            if op(left.ht, max) or op(left.hb, max):
                return False
        if bottomleft:
            if op(bottomleft.hl, max) or op(bottomleft.hr, max):
                return False
        # increase vertices
        if topleft:
            self.getTileTopLeft(tile).hb += amount
        if left:
            self.getTileLeft(tile).hr += amount
        if bottomleft:
            self.getTileBottomLeft(tile).ht += amount
        tile.hl += amount

    def increaseTileHB(self, tile, amount=32):
        ''' Increase the bottom corner of one tile and surrounding tiles '''
        max = tile.hb - amount
        bottomright = self.getTileBottomRight(tile)
        bottomleft = self.getTileBottomLeft(tile)
        bottom = self.getTileBottom(tile)
        # check tiles
        if amount > 0:
            op = le
        else:
            op = ge
        if op(tile.hl, max) or op(tile.hr, max):
            return False
        if bottomleft:
            if op(bottomleft.ht, max) or op(bottomleft.hb, max):
                    return False
        if bottomright:
            if op(bottomright.ht, max) or op(bottomright.hb, max):
                return False
        if bottom:
            if op(bottom.hl, max) or op(bottom.ht, max):
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
    
    def increaseTileHeight(self, tile, amount=32):
        ''' Increase the height of all the corners of a tile and the surrounding tiles affected corners '''
        self.increaseTileHB(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHR(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHL(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHT(self.tiles[tile.r][tile.c], amount)
        self.redraw()

    def decreaseTileHeight(self, tile, amount=-32):
        ''' Decrease the height of all the corners of a tile and the surrounding tiles affected corners '''
        self.increaseTileHB(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHR(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHL(self.tiles[tile.r][tile.c], amount)
        self.increaseTileHT(self.tiles[tile.r][tile.c], amount)
        self.redraw()
        
    def rotateTiles(self, direction='clockwise'):
        ''' rotate the tiles 
        Rotate all the vertices first, then the matrix of tiles
        '''
        #print(self.tiles[0])
        #print(self.tiles[1])
        if direction == 'clockwise':
            for r in self.tiles:
                for tile in r:
                    ht = tile.ht
                    hr = tile.hr
                    hb = tile.hb
                    hl = tile.hl
                    tile.ht = hl
                    tile.hr = ht
                    tile.hb = hr
                    tile.hl = hb
            rotated = list(zip(*self.tiles[::-1]))
        elif direction == 'counterclockwise':
            for r in self.tiles:
                for tile in r:
                    ht = tile.ht
                    hr = tile.hr
                    hb = tile.hb
                    hl = tile.hl
                    tile.ht = hr
                    tile.hr = hb
                    tile.hb = hl
                    tile.hl = ht
            rotated2 = list(zip(*self.tiles[::-1]))
            rotated1 = list(zip(*rotated2[::-1]))
            rotated = list(zip(*rotated1[::-1]))
        
        self.tiles = rotated
        for r, row in enumerate(self.tiles):
            for c, tile in enumerate(row):
                tile.r = r
                tile.c = c
        
                
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
        # draw tile
        flat = {'fill':self.colors[cl][0]}
        slopel = {'fill':self.colors[cl][1]}
        sloper = {'fill':self.colors[cl][2]}
        config = {'outline':self.colors[cl][3], 'activefill':'white', 'tags':f't{r}x{c}'}
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
            #self.canvas.create_polygon( *bottom, *right, *left, **sloper, **config) # this would be invisible
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
            self.canvas.create_polygon(*top,*bottom, *left, **slopel, **config)
            self.canvas.create_polygon( *top, *bottom, *right, **flat, **config)
            
        elif ht == hr and hb == hl and ht > hb: # slope upright
            self.canvas.create_polygon(*top, *right, *bottom, *left, **slopel, **config)
        elif ht == hr and hb == hl and ht < hb: # slope downleft
            self.canvas.create_polygon(*top, *right, *bottom, *left, **sloper, **config)
        elif ht == hl and hb == hr and ht > hb: # slope upleft
            self.canvas.create_polygon(*top, *right, *bottom, *left, **sloper, **config)
        elif ht == hl and hb == hr and ht < hb: # slope downright
            self.canvas.create_polygon(*top, *right, *bottom, *left, **slopel, **config)
            
        elif hl == hr and hb < hl and ht > hl: # slope up
            self.canvas.create_polygon(*top, *right, *bottom, *left, **slopel, **config)
            #self.canvas.create_polygon(*top, *right, *left, **slopel, **config)
            #self.canvas.create_polygon(*bottom, *right, *left, **slopel, **config)
        elif hl == hr and hb > hl and ht < hl: # slope down
            pass
            #self.canvas.create_polygon(*top, *right, *bottom, *left, **sloper, **config) # this would be invisible
            #self.canvas.create_polygon(*top, *right, *left, **sloper, **config)
            #self.canvas.create_polygon(*bottom, *right, *left, **sloper, **config)
        elif ht == hb and hl < ht and hr > ht: # slope right
            self.canvas.create_polygon(*top, *right, *bottom, *left, **slopel, **config)
            #self.canvas.create_polygon(*top, *bottom, *left, **slopel, **config)
            #self.canvas.create_polygon(*top, *bottom, *right, **slopel, **config)
        elif ht == hb and hl > ht and hr < ht: # slope left
            self.canvas.create_polygon(*top, *right, *bottom, *left, **sloper, **config)
            #self.canvas.create_polygon(*top, *bottom, *left, **sloper, **config)
            #self.canvas.create_polygon(*top, *bottom, *right, **sloper, **config)
            
        elif ht == hb and hl < ht and hr < ht: # slope down left/right
            self.canvas.create_polygon(*top, *bottom, *left, **slopel, **config)
            self.canvas.create_polygon(*top, *bottom, *right, **sloper, **config)
        elif hl == hr and ht < hl and hb < hl: # slope down top/bottom
            self.canvas.create_polygon(*top, *left, *right, **sloper, **config)
            self.canvas.create_polygon(*bottom, *left, *right, **slopel, **config)    
        else:
            raise Exception(f'Invalid slope {ht, hr, hb, hl}')

        # draw water
        if tile.ht < 0 or tile.hr < 0 or tile.hb < 0 or tile.hl < 0:
            top = (x, y)
            right = (x+(gw/2), y+(gh/2))
            bottom = (x, y+(gh))
            left = (x-(gw/2), y+(gh/2))
            config = {'fill':'blue', 'activefill':'lightblue', 'stipple':'gray50','tags':f't{r}x{c}'}
            if tile.ht < 0 and tile.hr < 0 and tile.hb < 0 and tile.hl < 0: # under water
                self.canvas.create_polygon(*top, *right, *bottom, *left, **config)
            elif tile.ht < 0 and (tile.hr < 0 or tile.hb <0 or tile.hl < 0): # if any two points are underwater
                self.canvas.create_polygon(*top, *right, *bottom, *left, **config)
            elif tile.hr < 0 and (tile.hb < 0 or tile.hl < 0):
                self.canvas.create_polygon(*top, *right, *bottom, *left, **config)
            elif tile.hb < 0 and tile.hl < 0:
                self.canvas.create_polygon(*top, *right, *bottom, *left, **config)
            elif tile.ht == tile.hb == 0 and tile.hr < 0: # slope right
                self.canvas.create_polygon(*top, *right, *bottom, **config)
            elif tile.ht == tile.hb == 0 and tile.hl < 0: # slope left
                self.canvas.create_polygon(*top, *left, *bottom, **config)
            elif tile.hl == tile.hr and tile.ht < 0: # slope top
                self.canvas.create_polygon(*left, *right, *top, **config)
            elif tile.hl == tile.hr == 0 and tile.hb < 0: # slope bottom
                self.canvas.create_polygon(*left, *right, *bottom, **config)
                
        # draw edges of map
        base = self.canvas.baseheight
        if not self.getTileBottomLeft(tile):
            leftx, lefty = left
            rightx, righty = bottom
            righth = hb + base *gs
            lefth = hl + base*gs
            rightdirt = (rightx, righty + righth)
            leftdirt = (leftx, lefty + lefth)
            rightwater = (rightx, righty - righth)
            leftwater = (leftx, lefty - lefth)
            if lefth == 0 and righth == 0: # flat
                pass # don't need to draw
            elif lefth >= 0 and righth >= 0: # dirt
                self.canvas.create_polygon(*left, *bottom, *rightdirt, *leftdirt, fill='#65532d')
            elif lefth <= 0 and righth <= 0: # water
                self.canvas.create_polygon(*left, *bottom, *rightwater, *leftwater, fill='blue', stipple='gray50')
                
                
        if not self.getTileBottomRight(tile):
            leftx, lefty = bottom
            rightx, righty = right
            lefth = hb + base*gs
            righth = hr + base*gs
            rightdirt = (rightx, righty + righth)
            leftdirt = (leftx, lefty + lefth)
            rightwater = (rightx, righty - righth)
            leftwater = (leftx, lefty - lefth)
            if lefth == 0 and righth == 0: # flat
                pass
            if lefth >= 0 and righth >= 0:
                self.canvas.create_polygon(*bottom, *right, *rightdirt, *leftdirt, fill='#8d7e47')
            elif lefth <= 0 and righth <= 0: # water
                self.canvas.create_polygon(*bottom, *right, *rightwater, *leftwater, fill='blue', stipple='gray50')
            
        self.canvas.tag_bind(f't{r}x{c}', '<Button-1>', self.tileClick)
        self.canvas.tag_bind(f't{r}x{c}', '<Button-3>', self.tileRightClick)
        
        
        if self.coordinates.get():
            self.canvas.create_text(*top, tags=f't{r}x{c}', text=f'{r}, {c}')
        
    
if __name__ == '__main__':
    import main
    
    
    
    
    
    