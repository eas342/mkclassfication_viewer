import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
import yaml
import glob
import os
import pdb


## Get the dictionary to convert spectral code to spectral type
spCodes = yaml.load(open('prog_data/stype_dict.yaml'))

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


