#!/usr/bin/env python

'''developer testing of reduceFlyScanData'''


import os
import glob
import localConfig
import reduceFlyData

MCA_CLOCK_FREQUENCY = localConfig.MCA_CLOCK_FREQUENCY
ARCHIVE_SUBDIR_NAME = 'archive'
V_f_gain = localConfig.FIXED_VF_GAIN
FULL_REDUCED_DATASET = -1
REDUCED_FLY_SCAN_BINS = localConfig.REDUCED_FLY_SCAN_BINS


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
