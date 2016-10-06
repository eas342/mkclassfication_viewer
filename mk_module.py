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
        self.tCode = float(self.basename[1:4])/10.0
        self.tClass = dictLookup(spCodes['Spectral Code'],self.tCode) ## temp class
        self.lCode = float(self.basename[5:7])/10.0
        self.lClass =  dictLookup(spCodes['Luminosity'],self.lCode) ## luminosity class
    
    def read_spec(self):
        dat = ascii.read(self.fullPath,names=['Wavelength','Flux'])
        goodp = dat['Flux'] > 0 ## only show non-zero points
        self.cleanDat = dat[goodp]

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

def make_type_table():
    fileL = glob.glob('../mklib/libnor36/*.rbn')
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
    #pdb.set_trace()
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
        
    t.write('prog_data/library_table.csv')   
    #for oneFile in fileL:
     #   column = 
    #for np.
