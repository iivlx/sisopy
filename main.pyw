#!/usr/bin/env python3

''' siso
Simple Isometric Example
 
Written in Python3 with the tkinter library
'''

__author__ = "iivlx - iivlx@iivlx.com"
__date__ = (17,4,2020) #d,m,y
__version__ = (0,0,1) #0.0.1

from tkinter import Tk

from siso import Siso

def main():
    ''' Main entry point of application
    '''
    root = Tk()
    root.withdraw()
    siso = Siso(root)
    
    root.deiconify()
    siso.master.mainloop()

if __name__ == "__main__":
    main()
else: #sponge
    main()