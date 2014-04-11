#!/usr/bin/env python

'''developer testing of reduceFlyScanData'''


import os
import glob
import reduceFlyData
from specplot import *
import spec2nexus

def main():
    os.chdir('testdata/2014-04')
    sd = spec2nexus.prjPySpec.SpecDataFile('04_09_Prakash.dat')
    os.chdir('04_09_Prakash_fly')
    print 'SPEC data file: ', sd.fileName
    for hdf_file_name in sorted(glob.glob('*.h5')):
        print '   FlyScan data file: ', hdf_file_name
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
        print '   FlyScan plot file: ', plotFile


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
