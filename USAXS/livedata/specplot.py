#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   read a SPEC data file and plot scan n using ploticus
'''

import os
import os.path
import sys
import subprocess
import shlex
import tempfile
import prjPySpec	# read SPEC data files


#@TODO: needs to be converted to 15ID-D
#@TODO: needs ploticus


PLOT_FORMAT = "png"
PLOTICUS = "/home/joule/USAXS/bin/pl"
PLOTFILE = "pete.png"
PLOTICUS_COMMAND_FILE = "pete.pl"
NO_POINTS_THRESHOLD = 400


def makePloticusPlot(scan, plotFile):
    '''plot scan n from the SPEC scan object'''
    plotData = zip(scan.data[scan.column_first], scan.data[scan.column_last])
    if len(plotData) == 0:
	raise Exception("No data to plot")
    #------------
    # http://ploticus.sourceforge.net/doc/prefab_lines_ex.html
    #------------
    pl = []
    xMin = xMax = yMin = yMax = None
    for (x, y) in plotData:
	pl.append("   %s  %s" % (x, y))
	if xMin == None:
	    xMin = xMax = x
	    yMin = yMax = y
	else:
	    if x < xMin: xMin = x
	    if y < yMin: yMin = y
	    if x > xMax: xMax = x
	    if y > yMax: yMax = y
    #---- write the ploticus data file
    ext = os.extsep + "pl"
    (f, dataFile) = tempfile.mkstemp(dir="/tmp", text=True, suffix=ext)
    f = open(dataFile, "w")
    f.write("\n".join(pl))
    f.close()
    #---- execute the ploticus command file using a "prefab" plot style
    name = "#%d: %s" % (scan.scanNum, scan.scanCmd)
    title = "%s, %s" % (scan.specFile, scan.date)
    command = PLOTICUS
    command += " -prefab lines"
    command += " data=%s x=1 y=2" % dataFile
    command += " xlbl=\"%s\"" % scan.column_first
    command += " ylbl=\"%s\"" % scan.column_last
    if len(plotData) >= NO_POINTS_THRESHOLD:
        command += " pointsym=\"none\""
    command += " name=\"%s\"" % name
    command += " title=\"%s\"" % title
    command += " -" + PLOT_FORMAT
    command += " -o " + plotFile
    lex = shlex.split(command)
    # run the command but gobble up stdout (make it less noisy)
    p = subprocess.Popen(lex, stdout=subprocess.PIPE)
    p.wait()
    os.remove(dataFile)


def openSpecFile(specFile):
    '''
    convenience routine so that others 
    do not have to import prjPySpec
    '''
    sd = prjPySpec.specDataFile(specFile)
    return sd


def findScan(sd, n):
    '''
    return the first scan with scan number "n" 
    from the spec data file object or None
    '''
    scan = None
    n = int(n)
    for t in sd.scans:
	if n == t.scanNum:
	    scan = t
	    break
    return scan


if __name__ == '__main__':
    specFile = '/share1/USAXS_data/2010-03/03_25.dat'
    scan_number = 1
    if len(sys.argv) == 4:
        (specFile, scan_number, plotFile) = sys.argv[1:4]
    else:
        print "usage: %s specFile scan_number plotFile" % sys.argv[0]
        sys.exit()
    specData = openSpecFile(specFile)
    scan = findScan(specData, scan_number)
    makePloticusPlot(scan, plotFile)
