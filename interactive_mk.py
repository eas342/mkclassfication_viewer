import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import tkFileDialog
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
    outX = np.array(x)
    outX[outX < xmin] = xmin
    outX[outX > xmax] = xmax
    return outX

class spectralSequence(object):
    """
    Reads in the available spectral types and allows you to cycle through them
    
    Parameters
    --------------------
    comparisonSpectrum: str
        A directory path of a target spectrum
    verbose: bool
        Whether to print extra info
    zoomState: str
        Whether to start zoomed 'In' or 'Out'
    nShow: int
        The number of reference spectra to show
    initialdir: str
        The directory where to search for new target spectrum for spectral typing 
    """
    def __init__(self,comparisonSpectrum=None,verbose=False,zoomState='In',nShow=2,
                initialdir='/Users/everettschlawin/Documents/jwst/nircam_photcal/general_photcal_code/output_rectified/NGC_2420'):
        
        self.verbose = verbose
        
        self.fileTable = ascii.read('prog_data/library_table.csv',data_start=1,
                                    header_start=0,delimiter=',')
        
        self.libraryDirectory = mk_module.libraryDirectory
        self.nTemp = len(self.fileTable)
        firstTIndex = int(self.nTemp / 2) ## start in the middle
        
        self._nIndex = nShow
        self._tIndex = firstTIndex - np.arange(nShow)
        
        ## Spectral code to Spectral type dictionary
        self.spCodes = yaml.load(open('prog_data/stype_dict.yaml'))
        
        ## Number of spectral types in table
        ## assumes two columns for spectral type code and spectral type name
        self.extraColumns = 2
        self.nLum = len(self.fileTable.colnames) - self.extraColumns
        self._lIndex = int(self.nLum - 1) * np.ones(nShow,dtype=np.int)
        
        ## Prepare the x,y and titles for 2 reference spec
        self.x = [None] * self._nIndex
        self.y = [None] * self._nIndex
        self.title = [None] * self._nIndex
        
        self.get_spec()
        
        self.make_mask_img() ## make a image of 1s and 0s for mask
        
        self.limits = [0.,3.]
        self.get_spec()
        self.xlabel = 'F$_\lambda$'
        self.ylabel = 'Wavelength ($\AA$)'
        self.initialdir=initialdir
        self.get_comparison_spec(comparisonSpectrum)
        self.zoomState = zoomState
        
        self.showLines = True
        self.specFeatures = ascii.read('prog_data/spec_features.csv')
    
    def right(self):
        self.change_lumclass(1)
    def left(self):
        self.change_lumclass(-1)
    def up(self):
        self.change_tempclass(1)
    def down(self):
        self.change_tempclass(-1)
    
    def get_comparison_spec(self,comparisonSpectrum):
        """ Gets a comparison spectrum for a given file name
        """
        if comparisonSpectrum == None:
            self.comparisonSpectrum = None
        else:
            self.comparisonSpectrum = comparisonSpectrum
            self.comparisonDat = ascii.read(comparisonSpectrum,names=['Wavelength','Flux'])
            self.comparisonName = os.path.splitext(os.path.basename(self.comparisonSpectrum))[0]
    
    def adjust_norm(self,adjust):
        """ 
        Adjusts the normalization of the target Spectrum (moving it up or down )
        """
        if self.comparisonSpectrum is not None:
            self.comparisonDat['Flux'] = self.comparisonDat['Flux'] + adjust
    
    def change_tempclass(self,amount):
        """ 
        Changes the temperature class by going up by amount in the index of the file Table
        """
        if not np.all(self._lIndex == self._lIndex[0]):
            ## Check that the reference stars have the same luminosity index
            self._lIndex = self._lIndex[0] * np.ones(self._nIndex,dtype=np.int)
            self._tIndex = self._tIndex[0] - np.arange(self._nIndex)
        
        self._tIndex = confine_range(self._tIndex + amount,0,self.nTemp-1)
        self.get_spec()
    
    def change_lumclass(self,amount):
        """ 
        Changes the luminosity class by going up by amount in the index of the file Table
        """
        if not np.all(self._tIndex == self._tIndex[0]):
            ## Check that the reference stars have the same temperature index
            self._lIndex = self._lIndex[0] - np.arange(self._nIndex)
            self._tIndex = self._tIndex[0] * np.ones(self._nIndex,dtype=np.int)
        
        self._lIndex = confine_range(self._lIndex + amount,0,self.nLum-1)
        self.get_spec()
    
    def get_spec(self):
        """
        Gets a mkspectrum if there is a spectrum with the requested temperature class index
        and luminosity class index
        """
        
        for indInd in range(self._nIndex):
            oneTIndex, oneLIndex = self._tIndex[indInd], self._lIndex[indInd]
            
            
            if np.all(self.fileTable.mask[oneTIndex][oneLIndex + self.extraColumns]) == True:
                if self.verbose == True:
                    print("No library spectrum at "+self.fileTable['Temperature_Class'][oneTIndex]+
                          " and "+self.fileTable.colnames[oneLIndex + self.extraColumns])
            else:
                basename = self.fileTable[oneTIndex][oneLIndex + self.extraColumns]
                oneFile = os.path.join(self.libraryDirectory,basename)
                specInfo = mk_module.mkspectrum(oneFile)
                specInfo.read_spec()
                
                self.x[indInd] = specInfo.cleanDat['Wavelength']
                self.y[indInd] = specInfo.cleanDat['Flux']
                
                self.title[indInd] = specInfo.tClass+' '+specInfo.lClass
    
    def print_to_file(self):
        """ Prints the assigned spectral type to file
        For now, it uses the spectral type of the top spectrum """
        if self.comparisonSpectrum != None:
            spType = self.title[0]
            with open('output/type_output.txt','a') as outFile:
                outFile.write(self.comparisonName+' '+spType+'\n')
    
    def make_mask_img(self):
        self.maskImg = np.zeros([self.nTemp,self.nLum])
        for columnInd, oneColumn in enumerate(self.fileTable.colnames[self.extraColumns:]):
            self.maskImg[:,columnInd] = self.fileTable.mask[oneColumn]
        #plt.imshow(sseq.maskImg,interpolation='none',cmap=plt.cm.YlOrRd)
    
    def do_plot(self,fig,axSpec,axClass):
        ## Plot the spectrum
        axSpec.cla()
        
        linePlots = []
        for indInd in range(self._nIndex):
            thisPlot = axSpec.plot(self.x[indInd],self.y[indInd] + 1. * (self._nIndex - 1 - indInd),label='St '+self.title[indInd])
            linePlots.append(thisPlot)
        
        axSpec.set_ylim(self.limits[0],self.limits[1])
        
        if self.zoomState == 'In':
            axSpec.set_xlim(3800,4600)
                        
        if self.comparisonSpectrum != None:
            comparisonName = os.path.splitext(os.path.basename(self.comparisonSpectrum))[0]
            axSpec.plot(self.comparisonDat['Wavelength'],self.comparisonDat['Flux'],
                        label=comparisonName)
        axSpec.legend(loc='lower right')
        
            
            
        ## Plot the key of spectral type and show what we're currently on
        if axClass.firstTimeThrough == True:
            axClass.imshow(self.maskImg,interpolation='nearest',cmap=plt.cm.YlOrRd)
            axClass.invert_yaxis()
            for indInd in range(self._nIndex):
                circle = mpatches.Circle([self._lIndex[indInd],self._tIndex[indInd]],1,color=linePlots[indInd][0].get_color())
                axClass.add_patch(circle)
            
            ## Replace the labels with actual terms
            fig.canvas.draw()
            showLumIndices = [0,3,5,8]
            showLumLabels = ['Ia','II','III','V']
            axClass.set_xticks(showLumIndices)
            axClass.set_xticklabels(showLumLabels)
            
            showTLabels = ['O6','B0','B5','A0','A5','F0','F5','G0','G5','K0','K5','M0','M5']
            showTIndices = []
            for oneTempClass in showTLabels:
                showTIndices.append(np.where(self.fileTable['Temperature_Class'] == oneTempClass)[0][0])
            axClass.set_yticks(showTIndices)
            axClass.set_yticklabels(showTLabels)
            
            axClass.set_xlabel('Lum Class')
            axClass.set_ylabel('Temp Class')
            axClass.firstTimeThrough = False
            
        else:
            for indInd in range(self._nIndex):
                axClass.patches[indInd].center = self._lIndex[indInd], self._tIndex[indInd]
        
        if self.showLines == True:
            for oneLine in self.specFeatures:
                showX = oneLine['Feature Wavelength']
                axSpec.plot([showX,showX],[1.0,1.1],color='black')
                axSpec.text(showX,1.1,oneLine['Feature Name'],rotation=45,
                            horizontalalignment='left',verticalalignment='bottom')
            
    def zoom(self):
        if self.zoomState == 'In':
            self.zoomState = 'Out'
        else:
            self.zoomState = 'In'
    
    def toggle_lines(self):
        self.showLines = not self.showLines
            
    
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
        self.helpWindow = None
    
    def update_plot(self):
        """
        update_plot clears the current plot and re-does it with the latest function
        object. Ideally, it would someday use some fancier motions to avoid
        having to clear and re-draw the plot
        """
        
        self.function.do_plot(self.fig,self.ax,self.axClass)
        self.fig.canvas.draw()
        self.canvas.draw()
    
    def on_key_event(self,event):
        """
        Tests the keyboard event to """
        if event.key == 'q' or event.key == 'Q':
            self.quit()
        elif event.key in ['right','left','up','down','u','j','o','z','l']:
            ## In this section, all changes will update the plot
            if event.key == 'right': self.function.right()
            elif event.key == 'left' : self.function.left()
            elif event.key == 'up' : self.function.up()
            elif event.key == 'down' : self.function.down()
            elif event.key == 'u': self.function.adjust_norm(+0.1)
            elif event.key == 'j': self.function.adjust_norm(-0.1)
            elif event.key == 'o': 
                filename = tkFileDialog.askopenfilename(initialdir=self.function.initialdir)
                self.function.get_comparison_spec(filename)
            elif event.key == 'z': self.function.zoom()
            elif event.key == 'l': self.function.toggle_lines()
            else: 
                print('Nonsensical place reached in code!')
                pdb.set_trace()
            self.update_plot()
        elif event.key == 'h':
            self.helpWindow = tk.Tk()
            TWidg = tk.Text(self.helpWindow)#,height=5,width=30)
            with open('docs/interactive_mk_help.txt','r') as helpFile:
                helpText = helpFile.readlines()
            TWidg.pack()
            TWidg.insert(tk.END, "".join(helpText))
        elif event.key == 'p': self.function.print_to_file()
        elif event.key == 'u': self.function.adjust_norm(+0.05)
        elif event.key == 'j': self.function.adjust_norm(-0.05)
        
        elif event.key == 's':
            self.fig.savefig('plots/current_fig.pdf',bbox_inches='tight',interpolation='none')
        else:
            print('  %s' % event.key)
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
    