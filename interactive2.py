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

class sinecurve(object):
    """ A simple sine curve class with amplitude and phase.
    This was just to create an interactive plotting widget and test it out 
    by varying the amplitude and phase of the sine curve with keyboard input """
    def __init__(self):
        self.x = np.linspace(0,2. * np.pi)
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
    """ This class is an application widget for interacting with matplotlib
    using tkinter"""
    def __init__(self, master):
        self.master = master
        #self.fig, self.ax = plt.subplots(figsize=(4,4))
        self.fig = mplfig.Figure(figsize=(4, 4))
        self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=master)
        
        self.canvas.get_tk_widget().pack()
        
        self.function = sinecurve()
        self.update_plot()
        self.canvas.mpl_connect('key_press_event', self.on_key_event)
    
    def update_plot(self):
        """
        update_plot clears the current plot and re-does it with the latest function
        object. Ideally, it would someday use some fancier motions to avoid
        having to clear and re-draw the plot
        """
        self.ax.cla()
        self.ax.plot(self.function.x,self.function.y)
        self.ax.set_ylim(-2,2)
        self.canvas.draw()
    
    def on_key_event(self,event):
        """
        Tests the keyboard event to """
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
        """ Quits the program """
        self.master.quit()
        self.master.destroy()

def main():
    """
    Main function that creates the tk object and runs it
    """
    root = tk.Tk()
    if sys.platform == 'darwin':
        #I find this useful since my OS X always puts python/tkinter in the background and I want it in the foreground
        os.system('''osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    
    app = App(root)
    tk.mainloop()

if __name__ == '__main__':
    """ If running from the command line, do the main loop """
    main()
    