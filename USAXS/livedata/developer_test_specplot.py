
'''developer routine to test specplot.py'''

import specplot
import sys

specFile = '/data/USAXS_data/2014-08/08_15_Tomography.dat'
scan_number = 21
plotFile = "/tmp/specplot.png"


specData = specplot.openSpecFile(specFile)
scan = specplot.findScan(specData, scan_number)
specplot.makeScanImage(scan, plotFile)
