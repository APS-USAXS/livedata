#!/usr/bin/env python

'''developer testing of reduceFlyScanData'''


import os                   #@UnusedImport
import glob                 #@UnusedImport
import localConfig          #@UnusedImport
import reduceFlyData        #@UnusedImport
from specplot import *      #@UnusedWildImport
import spec2nexus           #@UnusedImport
import numpy
import h5py
import math
import datetime

MCA_CLOCK_FREQUENCY = localConfig.MCA_CLOCK_FREQUENCY
ARCHIVE_SUBDIR_NAME = 'archive'
V_f_gain = localConfig.FIXED_VF_GAIN
FULL_REDUCED_DATASET = -1
REDUCED_FLY_SCAN_BINS = localConfig.REDUCED_FLY_SCAN_BINS

# def Prakash_test():
#     os.chdir('testdata/2014-04')
#     sd = spec2nexus.prjPySpec.SpecDataFile('04_09_Prakash.dat')
#     os.chdir('04_09_Prakash_fly')
#     print 'SPEC data file: ', sd.fileName
#     for hdf_file_name in sorted(glob.glob('*.h5')):
#         print '   FlyScan data file: ', hdf_file_name
#         scanNum = int(hdf_file_name[1:hdf_file_name.find('_')])
#         scan = sd.getScan(scanNum)
#         hdf = reduceFlyData.UsaxsFlyScan(hdf_file_name)
#         hdf.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
#         plotData = zip(hdf.rebinned['Q'], hdf.rebinned['R'])
#         pl = format_ploticus_data(plotData)
#         dataFile = write_ploticus_data_file(pl['data'])
#         plotFile = 'S%d_plot.png' % scanNum
#         
#         #---- execute the ploticus command file using a "prefab" plot style
#         run_ploticus_command_script(scan, dataFile, plotData, plotFile)
#         print '   FlyScan plot file: ', plotFile


# def reduction_test():
#     path = 'testdata/flyScanHdf5Files'
#     for hdf_file_name in sorted(glob.glob(os.path.join(path, '*.h5'))):
#         print '   FlyScan data file: ', hdf_file_name
#         hdf = reduceFlyData.UsaxsFlyScan(hdf_file_name)
#         hdf.reduce()
#         hdf.save(hdf_file_name, True, False)
#         #hdf.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
#         #plotData = zip(hdf.rebinned['Q'], hdf.rebinned['R'])
#         print 'done'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def main():
    #reduction_test()
    testpath = os.path.join('testdata', '2014-04', '04_14_Winans_fly', '*.h5')
    testpath = os.path.join('testdata', '*.h5')
   
    c = 0
    for hdf_file_name in sorted(glob.glob(testpath)):
        print hdf_file_name
        ufs = reduceFlyData.UsaxsFlyScan(hdf_file_name)
        c += 1
        hfile = os.path.join('/tmp', 'reduced_%d.h5' % c)

        #ufs.make_archive()
        #ufs.read_reduced()
        ufs.reduce()
        ufs.rebin(REDUCED_FLY_SCAN_BINS)
        ufs.save(hfile, 'full')
        ufs.save(hfile, REDUCED_FLY_SCAN_BINS)


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
