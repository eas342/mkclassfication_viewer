import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from astropy.table import Table
import yaml
import glob
import os
import pdb
import es_gen
import pandas as pd


## Get the dictionary to convert spectral code to spectral type
spCodes = yaml.safe_load(open('prog_data/stype_dict.yaml'))

defaultLibraryDirectory = '../mklib/libnor36'

def make_line_csv():
    """ Make as a CSV from the Excel line list """
    dat = pd.read_excel('prog_data/spec_features.xlsx')
    dat.to_csv('prog_data/spec_features.csv',index=False)

def dictLookup(dict,item):
    if item in dict:
        output = dict[item]
    else:
        print("Couldn't find "+str(item)+' so returning None')
        output = None
    return output
    

class mkspectrum(object):
    """
    Finds the spectral and luminosity codes used by mkclass
    Converts these to spectral type
    """
    def __init__(self,oneFile):
        self.fullPath = oneFile
        self.basename = os.path.basename(oneFile)
        tCodeText = self.basename[1:4]
        self.tCode = float(tCodeText)/10.0
        self.tClass = dictLookup(spCodes['Spectral Code'],self.tCode) ## temp class
        self.lCode = float(self.basename[5:7])/10.0
        self.lClass =  dictLookup(spCodes['Luminosity'],self.lCode) ## luminosity class
    
    def read_spec(self):
        dat = ascii.read(self.fullPath,names=['Wavelength','Flux'])
        goodp = dat['Flux'] > 0 ## only show non-zero points
        self.cleanDat = dat[goodp]
        self.origDat = dat

def plot_seq():
    """ Goes through the sequence in the library and makes plots of the spectra"""
    fileL = glob.glob(libraryDirectory+'/*l50p00.rbn')
    
    #for oneFile in [fileL[0]]:
    for oneFile in fileL:
        plt.close('all')
        fig, ax = plt.subplots(figsize=(8,5))
        
        specInfo = mkspectrum(oneFile) ## spectral info
        specInfo.read_spec()
        ax.plot(specInfo.cleanDat['Wavelength'],specInfo.cleanDat['Flux'])
        
        ax.set_title(specInfo.tClass+' '+specInfo.lClass)
        ax.set_ylabel('F$_\lambda$')
        ax.set_xlabel('Wavelength ($\AA$)')
        ax.set_ylim(0.1,2)
        fig.savefig('plots/main_sequence/'+os.path.splitext(specInfo.basename)[0]+'.pdf')

def normalizeTemplates(doPlot=False):
    """
    This normalizes the template spectrum in the library the same way I normalized
    the spectrum from hectospec
    """
    fileL = glob.glob('../mklib/libnor36/*.rbn')
    
    startsets = np.arange(3500,6000,150) ## Sets of regions to do polynomial fits over
    polyord = 5 # polynomial order for de-trending the spectrum
    
    for oneFile in [fileL[0]]:
        specInfo = mkspectrum(oneFile)
        specInfo.read_spec()
        
        
        xplt = specInfo.origDat['Wavelength']
        
        
        yorig = specInfo.origDat['Flux']
    
        # Set up the divided array
        yfit = np.zeros_like(yorig)
        ydivide = np.zeros_like(yorig)
    
        for setstart in startsets:
        
            fitp = np.where((xplt > setstart) & (xplt < (setstart + 150)))
            #pdb.set_trace()
            coeff = es_gen.robust_poly(xplt[fitp],yorig[fitp],polyord,sigreject=5.0)
            ymod = np.poly1d(coeff)
            # Convolve data
            yfit[fitp] = ymod(xplt[fitp])
            ydivide[fitp] = yorig[fitp]/ymod(xplt[fitp])
        
        if doPlot == True:
            fig, ax = plt.subplots(figsize=(15,5))
            ax.plot(xplt,yorig,label='Original')
            ax.plot(xplt,yfit,label='Fit')
            ax.legend()
            plt.show()
    
    

def make_type_table(library='libnor36'):
    fileL = glob.glob('../mklib/{}/t???l??p??.rbn'.format(library))
    tCodes,tTypes = [], [] ## temperature codes and class
    lCodes = [] ## luminosity codes
    for oneFile in fileL:
        specInfo = mkspectrum(oneFile)
        tCodes.append(specInfo.tCode)
        tTypes.append(specInfo.tClass)
        lCodes.append(specInfo.lCode)
        
    uniqTCodes, uniqTIndices = np.unique(tCodes,return_index=True)
    nUniqT = uniqTCodes.shape[0]
    uniqlCodes = np.unique(lCodes)
    
    t = Table()
    
    t['Temperature_Class'] = np.array(tTypes)[uniqTIndices]
    t['Temperature_Code'] = uniqTCodes
    for oneLuminosity in uniqlCodes:
        t[str(oneLuminosity)] = np.empty(nUniqT,dtype=object)
    
    for oneFile in fileL:
        specInfo = mkspectrum(oneFile)
        row = (specInfo.tCode == t['Temperature_Code'])
        column = (str(specInfo.lCode) == np.array(t.colnames))
        
        if (np.sum(row) == 1) & (np.sum(column) == 1):
            t[np.where(row)[0][0]][np.where(column)[0][0]] = specInfo.basename
        else:
            print("File "+oneFile+" couldn't be placed in the table")
            pdb.set_trace()
        
    t.write('prog_data/library_table_{}.csv'.format(library))   
    #for oneFile in fileL:
     #   column = 
    #for np.
