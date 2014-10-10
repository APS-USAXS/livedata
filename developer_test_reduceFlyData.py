
'''developer routine to test reduceFlyData.py'''

import reduceFlyData
import sys

sys.argv = [sys.argv[0],]
#sys.argv.append( '-h' )
#sys.argv.append( '-V' )

sys.argv.append('')

testglob = 'testdata/flyscan_modes/*.h5'
testglob = 'testdata/flyscan_modes/S18_FS_Fixed*.h5'    # from day with no beam, this dataset has problems!
testglob = 'testdata/flyscan_modes/*_PSO_Fixed*.h5'     # from day with no beam 
testglob = 'testdata/flyscan_modes/S39_Blank*.h5'       # 2014-08-13, fly scan mode=1
testglob = 'testdata/flyscan_modes/S44_GC_Adam*.h5'     # 2014-08-13, fly scan mode=1
# testglob = 'testdata/flyscan_modes/S19_FS_Fixed*.h5'
testglob = 'testdata/fly/08_14_NIST_TRIP_fly/S48*.h5'
testglob = 'testdata/fly/10_09_Prisk_fly/S5_Glass_Blank.h5'

import glob
for hdf5_file in glob.glob(testglob):
    sys.argv[1] = hdf5_file
    reduceFlyData.command_line_interface()