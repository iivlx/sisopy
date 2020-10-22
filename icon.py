#!/usr/bin/env python3

''' IIVLX Icon '''

from tkinter import (PhotoImage, TclError)

IIVLXICO = """R0lGODlhIAAgAPcAAAAAAAAAMwAAZgAAmQAAzAAA/wArAAArMwArZgArmQArzAAr/
wBVAABVMwBVZgBVmQBVzABV/wCAAACAMwCAZgCAmQCAzACA/wCqAACqMwCqZgCqmQCqzACq/wDVAADV
MwDVZgDVmQDVzADV/wD/AAD/MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMrADMrMzMrZjM
rmTMrzDMr/zNVADNVMzNVZjNVmTNVzDNV/zOAADOAMzOAZjOAmTOAzDOA/zOqADOqMzOqZjOqmTOqzD
Oq/zPVADPVMzPVZjPVmTPVzDPV/zP/ADP/MzP/ZjP/mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YrA
GYrM2YrZmYrmWYrzGYr/2ZVAGZVM2ZVZmZVmWZVzGZV/2aAAGaAM2aAZmaAmWaAzGaA/2aqAGaqM2aq
ZmaqmWaqzGaq/2bVAGbVM2bVZmbVmWbVzGbV/2b/AGb/M2b/Zmb/mWb/zGb//5kAAJkAM5kAZpkAmZk
AzJkA/5krAJkrM5krZpkrmZkrzJkr/5lVAJlVM5lVZplVmZlVzJlV/5mAAJmAM5mAZpmAmZmAzJmA/5
mqAJmqM5mqZpmqmZmqzJmq/5nVAJnVM5nVZpnVmZnVzJnV/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwAM
8wAZswAmcwAzMwA/8wrAMwrM8wrZswrmcwrzMwr/8xVAMxVM8xVZsxVmcxVzMxV/8yAAMyAM8yAZsyA
mcyAzMyA/8yqAMyqM8yqZsyqmcyqzMyq/8zVAMzVM8zVZszVmczVzMzV/8z/AMz/M8z/Zsz/mcz/zMz
///8AAP8AM/8AZv8Amf8AzP8A//8rAP8rM/8rZv8rmf8rzP8r//9VAP9VM/9VZv9Vmf9VzP9V//+AAP
+AM/+AZv+Amf+AzP+A//+qAP+qM/+qZv+qmf+qzP+q///VAP/VM//VZv/Vmf/VzP/V////AP//M///Z
v//mf//zP///wAAAAAAAAAAAAAAACH5BAEAAPwALAAAAAAgACAAAAhzAPcJHEiwoMGDCBMqXMiwocOH
DTPFAECxosWLAFZkYjgRo8eLDCd9HAlADMSCFU8yTKlSIcuWCF/CNChzJsGaNgXizLnTZs+ZP2EGbTl
UZdGTRyEmfbjUYdOGT1dSbKmMJEmNCa1qTZhJ60iTOcOKHSswIAA7"""

def loadIcon(root, toplevel, icondata):
    ''' set the window icon
    icondata is base64 encoded gif
    '''
    try:
        icon = PhotoImage(data=icondata)
        root.call('wm', 'iconphoto', toplevel._w, icon)
    except TclError as err:
        if err.args[0] == 'couldn\'t recognize image data':
            pass # this is non-fatal, we are missing the icon
        else:
            raise err # probably fatal errorv