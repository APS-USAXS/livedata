#!/usr/bin/env python

'''repair miscalculated fly scan data reduction from April 2014'''


import os
import glob
import localConfig
import reduceFlyData
import stat
import shutil


MCA_CLOCK_FREQUENCY = localConfig.MCA_CLOCK_FREQUENCY
ARCHIVE_SUBDIR_NAME = 'archive'
V_f_gain = localConfig.FIXED_VF_GAIN
FULL_REDUCED_DATASET = -1
REDUCED_FLY_SCAN_BINS = localConfig.REDUCED_FLY_SCAN_BINS


def copy_from_archive(archive_path, hfile):
    target_path = os.path.abspath(os.path.join(archive_path, '..'))
    source_file = os.path.abspath(os.path.join(archive_path, hfile))
    target_file = os.path.abspath(os.path.join(target_path, hfile))
    shutil.copy2(source_file, target_file)
    mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
    os.chmod(target_file, mode)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def main():
    owd = os.getcwd()
    testpath = os.path.join('testdata', '2014-04', '*_fly')
    for path in sorted(glob.glob(testpath)):
        os.chdir(path)
        for hfile in sorted(glob.glob('S*.h5')):
            print path, hfile
            copy_from_archive(ARCHIVE_SUBDIR_NAME, hfile)
            ufs = reduceFlyData.UsaxsFlyScan(hfile)
            #ufs.make_archive()
            #ufs.read_reduced()
            ufs.reduce()
            ufs.rebin(REDUCED_FLY_SCAN_BINS)
            ufs.save(hfile, 'full')
            ufs.save(hfile, REDUCED_FLY_SCAN_BINS)
        os.chdir(owd)
    



if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision: 1011 $
# $URL$
# $Id$
########### SVN repository information ###################
