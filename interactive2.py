import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backend_bases import key_press_handler
import matplotlib.patches as mpatches
import os
import sys
import warnings
from astropy.io import ascii
import pdb
import glob
import yaml
import mk_module



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
def confine_range(x,xmin,xmax):
    """ 
    Simple function keeps x between xmin and xmax
    If larger or smaller than the limits, it is kept at the boundary
    """
    if x < xmin:
        outX = xmin
    elif x > xmax:
        outX = xmax
    else:
        outX = x
    return outX

class spectralSequence(object):
    """
    Reads in the available spectral types and allows you to cycle through them
    """
    def __init__(self,comparisonSpectrum=None):
        self._typecode = 31.
        self._lumcode = 5
        
        self.fileTable = ascii.read('prog_data/library_table.csv',data_start=1,
                                    header_start=0,delimiter=',')
        
        self.libraryDirectory = mk_module.libraryDirectory
        self.nTemp = len(self.fileTable)
        self._tIndex = int(self.nTemp / 2) ## start in the middle
        
        ## Spectral code to Spectral type dictionary
        self.spCodes = yaml.load(open('prog_data/stype_dict.yaml'))
        
        ## Number of spectral types in table
        ## assumes two columns for spectral type code and spectral type name
        self.extraColumns = 2
        self.nLum = len(self.fileTable.colnames) - self.extraColumns
        self._lIndex = int(self.nLum - 1)
        
        self.get_spec()
        
        self.make_mask_img() ## make a image of 1s and 0s for mask
        
        self.limits = [0.,2]
        self.get_spec()
        self.xlabel = 'F$_\lambda$'
        self.ylabel = 'Wavelength ($\AA$)'
        if comparisonSpectrum == None:
            self.comparisonSpec = None
        else:
            self.comparisonSpec = comparisonSpectrum
            self.comparisonDat = ascii.read(comparisonSpectrum,names=['Wavelength','Flux'])
    
    def right(self):
        self.change_lumclass(1)
    def left(self):
        self.change_lumclass(-1)
    def up(self):
        self.change_tempclass(1)
    def down(self):
        self.change_tempclass(-1)
    
    def change_tempclass(self,amount):
        """ 
        Changes the temperature class by going up by amount in the index of the file Table
        """
        self._tIndex = confine_range(self._tIndex + amount,0,self.nTemp-1)
        self.get_spec()
    
    def change_lumclass(self,amount):
        """ 
        Changes the luminosity class by going up by amount in the index of the file Table
        """
        self._lIndex = confine_range(self._lIndex + amount,0,self.nLum-1)
        self.get_spec()        
    
    def get_spec(self):
        """
        Gets a mkspectrum if there is a spectrum with the requested temperature class index
        and luminosity class index
        """
        if self.fileTable.mask[self._tIndex][self._lIndex + self.extraColumns] == True:
            print("No library spectrum at "+self.fileTable['Temperature_Class'][self._tIndex]+
                  " and "+self.fileTable.colnames[self._lIndex + self.extraColumns])
        else:
            basename = self.fileTable[self._tIndex][self._lIndex + self.extraColumns]
            oneFile = os.path.join(self.libraryDirectory,basename)
            specInfo = mk_module.mkspectrum(oneFile)
            specInfo.read_spec()
        
            self.x = specInfo.cleanDat['Wavelength']
            self.y = specInfo.cleanDat['Flux']
            
            self.title = specInfo.tClass+' '+specInfo.lClass
    
    def make_mask_img(self):
        self.maskImg = np.zeros([self.nTemp,self.nLum])
        for columnInd, oneColumn in enumerate(self.fileTable.colnames[self.extraColumns:-1]):
            self.maskImg[:,columnInd] = self.fileTable.mask[oneColumn]
        #plt.imshow(sseq.maskImg,interpolation='none',cmap=plt.cm.YlOrRd)
    
    def do_plot(self,axSpec,axClass):
        ## Plot the spectrum
        axSpec.cla()
        axSpec.plot(self.x,self.y,label='Standard')
        axSpec.set_ylim(self.limits[0],self.limits[1])
        axSpec.set_title(self.title)
        
        if self.comparisonSpec != None:
            axSpec.plot(self.comparisonDat['Wavelength'],self.comparisonDat['Flux'],
                        label='Input Spec')
            axSpec.legend(loc='lower right')
            
        ## Plot the key of spectral type and show what we're currently on
        if axClass.firstTimeThrough == True:
            axClass.imshow(self.maskImg,interpolation='nearest',cmap=plt.cm.YlOrRd)
            axClass.invert_yaxis()
            circle = mpatches.Circle([self._lIndex,self._tIndex],1)
            axClass.add_patch(circle)
            
            axClass.set_xlabel('Lum Class')
            axClass.set_ylabel('Temp Class')
            axClass.firstTimeThrough = False
            
        else:
            axClass.patches[0].center = self._lIndex, self._tIndex
            
    
class App(object):
    """ This class is an application widget for interacting with matplotlib
    using tkinter"""
    def __init__(self, master,apptestmode=False,comparisonSpectrum=None):
        self.master = master
        #self.fig, self.ax = plt.subplots(figsize=(4,4))
        self.fig = mplfig.Figure(figsize=(20, 6))
        self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        self.axClass = self.fig.add_axes([0.9,0.1,0.1,0.8])
        self.axClass.firstTimeThrough = True ## note to set up for first time
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, master=master)
        
        self.canvas.get_tk_widget().pack()
        if apptestmode:
            self.function = sinecurve()
        else:
            self.function = spectralSequence(comparisonSpectrum=comparisonSpectrum)
        self.update_plot()
        self.canvas.mpl_connect('key_press_event', self.on_key_event)
        
    
    def update_plot(self):
        """
        update_plot clears the current plot and re-does it with the latest function
        object. Ideally, it would someday use some fancier motions to avoid
        having to clear and re-draw the plot
        """
        
        self.function.do_plot(self.ax,self.axClass)
        
        self.fig.canvas.draw()
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
        elif event.key == 's':
            self.fig.savefig('plots/current_fig.pdf',bbox_inches='tight',interpolation='none')
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
    del app
    del root

if __name__ == '__main__':
    """ If running from the command line, do the main loop """
    main()
    