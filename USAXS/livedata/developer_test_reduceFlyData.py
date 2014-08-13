
'''developer routine to test reduceFlyData.py'''

import reduceFlyData
import sys

sys.argv = [sys.argv[0],]
#sys.argv.append( '-h' )
#sys.argv.append( '-V' )

sys.argv.append('')

testglob = 'testdata/flyscan_modes/*.h5'
testglob = 'testdata/flyscan_modes/*S18_FS_Fixed.h5'

import glob
for hdf5_file in glob.glob(testglob):
    sys.argv[1] = hdf5_file
    reduceFlyData.command_line_interface()
