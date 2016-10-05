import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backend_bases import key_press_handler
import os
import sys
import warnings
import pdb
pi = np.pi

class sinecurve(object):
    def __init__(self):
        self.x = np.linspace(0,6.28)
        self.phase = 0
        self.amplitude = 1.0
        self.evaluate()
    
    def evaluate(self):
        self.y = self.amplitude * np.sin(self.x - self.phase)
    
    def expand(self,amount):
        self.amplitude = self.amplitude * amount
        self.evaluate()
    
    def shift(self,amount):
        self.phase = self.phase + amount
        self.evaluate()
        
class App(object):
    def __init__(self, master):
        self.master = master
        #self.fig, self.ax = plt.subplots(figsize=(4,4))
        self.fig = mplfig.Figure(figsize=(4, 4))
        self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=master)
        self.ax.grid(False)
        self.canvas.get_tk_widget().pack()
        
        self.function = sinecurve()
        self.update_plot()
        self.canvas.mpl_connect('key_press_event', self.on_key_event)
    
    def update_plot(self):
        self.ax.cla()
        self.ax.plot(self.function.x,self.function.y)
        self.ax.set_ylim(-2,2)
        self.canvas.draw()
    
    def on_key_event(self,event):
        if event.key == 'q' or event.key == 'Q':
            self.quit()
        elif event.key in ['right','left','up','down']:
            if event.key == 'right': self.function.shift(0.1)
            elif event.key == 'left' : self.function.shift(-0.1)
            elif event.key == 'up' : self.function.expand(1.1)
            elif event.key == 'down' : self.function.expand(0.9)
            else: 
                print('Nonsensical place reached in code!')
                pdb.set_trace()
            self.update_plot()
        else:
            print('you pressed %s' % event.key)
        #key_press_handler(event, self.canvas, toolbar)
    
    def quit(self):
        self.master.quit()
        self.master.destroy()

def main():
    root = tk.Tk()
    if sys.platform == 'darwin':
        #I find this useful since my OS X always puts python/tkinter in the background and I want it in the foreground
        os.system('''osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    
    app = App(root)
    tk.mainloop()

if __name__ == '__main__':
    main()