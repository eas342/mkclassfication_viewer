#!/usr/bin/env python

import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

root = Tk.Tk()
root.wm_title("Embedding in TK")

fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
t = arange(0.0, 3.0, 0.01)

#global s
s = sin(2*pi*t)

ax.plot(t, s)



# a tk.DrawingArea
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)



def on_key_event(event,s):
    if event.key == 'Q' or event.key == 'q':
        _quit()
    elif event.key == 'u':
        #fig.clf()
        
        s = s + 0.1
        #canvas.show()
        #canvas.blit(ax)
    elif event.key == 'j':
        s = s - 0.1
    ax.cla()
    ax.plot(t, s)
    canvas.draw()
    print('you pressed %s' % event.key)
    key_press_handler(event, canvas, toolbar)
    

canvas.mpl_connect('key_press_event', lambda event: on_key_event(event,s))


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = Tk.Button(master=root, text='Quit (Q)', command=_quit)
button.pack(side=Tk.BOTTOM)

Tk.mainloop()
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.
