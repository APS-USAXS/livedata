
'''developer routine to test specplot.py'''

import specplot
import sys

specFile = '/data/USAXS_data/2014-08/08_14_NIST_TRIP.dat'
scan_number = 619
plotFile = "/tmp/specplot.png"


specData = specplot.openSpecFile(specFile)
scan = specplot.findScan(specData, scan_number)
specplot.makeScanImage(scan, plotFile)
