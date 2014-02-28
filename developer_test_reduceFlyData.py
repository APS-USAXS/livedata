
'''developer routine to test reduceFlyData.py'''

import reduceFlyData
import sys

sys.argv = [sys.argv[0],]
#sys.argv.append( '-h' )
#sys.argv.append( '-V' )

sys.argv.append('')

import glob
for hdf5_file in glob.glob('testdata/*.h5'):
  sys.argv[1] = hdf5_file
  reduceFlyData.main()
