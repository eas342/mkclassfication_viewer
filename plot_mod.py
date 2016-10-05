import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from astropy.table import Table
import yaml
import glob
import os
import pdb


## Get the dictionary to convert spectral code to spectral type
spCodes = yaml.load(open('prog_data/stype_dict.yaml'))

libraryDirectory = '../mklib/libnor36'

class mkspectrum(object):
    """
    Finds the spectral and luminosity codes used by mkclass
    Converts these to spectral type
    """
    def __init__(self,oneFile):
        self.basename = os.path.basename(oneFile)
        self.tCode = float(self.basename[1:4])/10.0
        self.tClass = spCodes['Spectral Code'][self.tCode] ## temp class
        self.lCode = float(self.basename[5:7])/10.0
        self.lClass =  spCodes['Luminosity'][self.lCode] ## luminosity class
    

def plot_seq():
    """ Goes through the sequence in the library and makes plots of the spectra"""
    fileL = glob.glob(libraryDirectory+'/*l50p00.rbn')
    
    #for oneFile in [fileL[0]]:
    for oneFile in fileL:
        plt.close('all')
        #pdb.set_trace()
        dat = ascii.read(oneFile,names=['Wavelength','Flux'])
        fig, ax = plt.subplots(figsize=(8,5))
        goodp = dat['Flux'] > 0 ## only show non-zero points
        ax.plot(dat['Wavelength'][goodp],dat['Flux'][goodp])
        specInfo = mkspectrum(oneFile) ## spectral info
        
        ax.set_title(specInfo.tClass+' '+specInfo.lClass)
        ax.set_ylabel('F$_\lambda$')
        ax.set_xlabel('Wavelength ($\AA$)')
        ax.set_ylim(0.1,2)
        fig.savefig('plots/main_sequence/'+os.path.splitext(specInfo.basename)[0]+'.pdf')

def make_type_table():
    fileL = glob.glob('..mklib/libnor36/*.rbn')
    tcodes = [] ## temperature codes
    lcodes = [] ## luminosity codes
    for oneFile in fileL:
        basename = os.path.basename(oneFile)
        tempCode = float(basename[1:4])/10.0
        tcodes.append(tempCode)
        lCode = float(basename[5:7])/10.0
        lClass = spCodes['Luminosity'][lCode] ## luminosity class
        
    uniqCodes = np.unique(tcodes)
    t = Table()
    #for np.
