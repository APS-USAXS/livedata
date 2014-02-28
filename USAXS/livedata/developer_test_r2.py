
'''developer routine to test r2.py'''

import r2
import sys

sys.argv = [sys.argv[0],]
#sys.argv.append( '-h' )
#sys.argv.append( '-V' )

sys.argv.append('')

import glob
for hdf5_file in glob.glob('testdata/*.h5'):
  sys.argv[1] = hdf5_file
  r2.main()
