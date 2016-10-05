import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backend_bases import key_press_handler
import os
import sys
import warnings
from astropy.io import ascii
import pdb
import glob
import yaml

class sinecurve(object):
    """ A simple sine curve class with amplitude and phase.
    This was just to create an interactive plotting widget and test it out 
    by varying the amplitude and phase of the sine curve with keyboard input """
    def __init__(self):
        self.x = np.linspace(0,2. * np.pi)
        self.phase = 0
        self.amplitude = 1.0
        self.evaluate()
        self.limits = [-2,2]
    
    def right(self):
        self.shift(0.1)
    def left(self):
        self.shift(-0.1)
    def up(self):
        self.expand(1.1)
    def down(self):
        self.expand(0.9)
    
    def evaluate(self):
        self.y = self.amplitude * np.sin(self.x - self.phase)
        self.title = 'amp = {0:0.3f}, phase = {1:0.3f}'.format(self.amplitude,self.phase)
    
    def expand(self,amount):
        self.amplitude = self.amplitude * amount
        self.evaluate()
    
    def shift(self,amount):
        self.phase = self.phase + amount
        self.evaluate()

class spectralSequence(object):
    """
    Reads in the available spectral types and allows you to cycle through them
    """
    def __init__(self):
        self._typecode = 31.
        self._lumcode = 5
        
        self.fileList = glob.glob('../mklib/libnor36/*l50p00.rbn')
        self.nFiles = len(self.fileList)
        self.spCodes = yaml.load(open('prog_data/stype_dict.yaml'))
        
        self._simpleIndex = 30
        self.get_spec()
        self.limits = [0.,2]
        self.get_spec()
        self.xlabel = 'F$_\lambda$'
        self.ylabel = 'Wavelength ($\AA$)'
    
    def right(self):
        print('no Lum yet')
    def left(self):
        print('no Lum yet')
    def up(self):
        self.earlier()
    def down(self):
        self.later()
    
    def earlier(self):
        if self._simpleIndex <= 0:
            self._simpleIndex = 0
        else:
            self._simpleIndex -= 1
        self.get_spec()
    
    def later(self):
        if self._simpleIndex >= self.nFiles-1:
            self._simpleIndex = self.nFiles-1
        else:
            self._simpleIndex += 1
        self.get_spec()
    
    def get_spec(self):
        oneFile = self.fileList[self._simpleIndex]
        dat = ascii.read(oneFile,names=['Wavelength','Flux'])
        goodp = dat['Flux'] > 0 ## only show non-zero points
        self.x = dat['Wavelength'][goodp]
        self.y = dat['Flux'][goodp]
        basename = os.path.basename(oneFile)
        spcode = float(basename[1:4])/10.0
        self.tClass = self.spCodes['Spectral Code'][spcode] ## temp class
        lCode = float(basename[5:7])/10.0
        self.lClass = self.spCodes['Luminosity'][lCode] ## luminosity class
        self.title = self.tClass+' '+self.lClass
    

    def plot_seq():
        """ Goes through the sequence in the library and makes plots of the spectra"""
        fileL = glob.glob('../mklib/libnor36/*l50p00.rbn')

        #for oneFile in [fileL[0]]:
        for oneFile in fileL:
            plt.close('all')
            #pdb.set_trace()
            dat = ascii.read(oneFile,names=['Wavelength','Flux'])
            fig, ax = plt.subplots(figsize=(8,5))
            goodp = dat['Flux'] > 0 ## only show non-zero points
            ax.plot(dat['Wavelength'][goodp],dat['Flux'][goodp])
            basename = os.path.basename(oneFile)
            spcode = float(basename[1:4])/10.0
            tClass = spCodes['Spectral Code'][spcode] ## temp class
            lCode = float(basename[5:7])/10.0
            lClass = spCodes['Luminosity'][lCode] ## luminosity class
            ax.set_title(tClass+' '+lClass)
            ax.set_ylabel('F$_\lambda$')
            ax.set_xlabel('Wavelength ($\AA$)')
            ax.set_ylim(0.1,2)
            fig.savefig('plots/main_sequence/'+os.path.splitext(basename)[0]+'.pdf')


    
class App(object):
    """ This class is an application widget for interacting with matplotlib
    using tkinter"""
    def __init__(self, master,apptestmode=False):
        self.master = master
        #self.fig, self.ax = plt.subplots(figsize=(4,4))
        self.fig = mplfig.Figure(figsize=(15, 4))
        self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=master)
        
        self.canvas.get_tk_widget().pack()
        if apptestmode:
            self.function = sinecurve()
        else:
            self.function = spectralSequence()
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
        self.ax.set_ylim(self.function.limits[0],self.function.limits[1])
        self.ax.set_title(self.function.title)
        self.canvas.draw()
    
    def on_key_event(self,event):
        """
        Tests the keyboard event to """
        if event.key == 'q' or event.key == 'Q':
            self.quit()
        elif event.key in ['right','left','up','down']:
            if event.key == 'right': self.function.right()
            elif event.key == 'left' : self.function.left()
            elif event.key == 'up' : self.function.up()
            elif event.key == 'down' : self.function.down()
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

def main(**kwargs):
    """
    Main function that creates the tk object and runs it
    """
    root = tk.Tk()
        
    app = App(root,**kwargs)
    if sys.platform == 'darwin':
        #I find this useful since my OS X always puts python/tkinter in the background and I want it in the foreground
        os.system('''osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    tk.mainloop()

if __name__ == '__main__':
    """ If running from the command line, do the main loop """
    main()
    