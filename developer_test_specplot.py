
'''developer routine to test specplot.py'''

import specplot
import os, sys

specFile = '/share1/old_USAXS_data/2014-08/08_15_Tomography.dat'
scan_number = 21
specFile = '/share1/USAXS_data/2015-01/02_07_Testing.dat'
scan_number = 86
plotFile = "/tmp/specplot.png"

sys.argv.append(specFile)
sys.argv.append(str(scan_number))
sys.argv.append(plotFile)

# specData = specplot.openSpecFile(specFile)
# scan = specplot.findScan(specData, scan_number)
# specplot.makeScanImage(scan, plotFile)
specplot.main()
