#!/usr/bin/env python

'''developer testing of reduceFlyScanData'''


import os
import glob
import reduceFlyData
from specplot import *
import spec2nexus

def main():
    os.chdir('testdata/2014-04-09')
    sd = spec2nexus.prjPySpec.SpecDataFile('04_09_Prakash.dat')
    os.chdir('04_09_Prakash_fly')
    for hdf_file_name in glob.glob('*.h5'):
        scanNum = int(hdf_file_name[1:hdf_file_name.find('_')])
        scan = sd.getScan(scanNum)
        hdf = reduceFlyData.UsaxsFlyScan(hdf_file_name)
        hdf.rebin(250)      # does not store any data back to HDF5 file
        plotData = zip(hdf.rebinned['Q'], hdf.rebinned['R'])
        pl = format_ploticus_data(plotData)
        dataFile = write_ploticus_data_file(pl['data'])
        plotFile = 'S%d_plot.png' % scanNum
     
        #---- execute the ploticus command file using a "prefab" plot style
        run_ploticus_command_script(scan, dataFile, plotData, plotFile)


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
