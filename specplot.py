#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   read a SPEC data file and plot scan n
'''

import os
import os.path
import sys
import subprocess
import shlex
import tempfile
import prjPySpec	# read SPEC data files


PLOT_FORMAT = "png"
PLOTICUS = "/home/joule/USAXS/bin/pl"
PLOTFILE = "pete.png"
PLOTICUS_COMMAND_FILE = "pete.pl"
NO_POINTS_THRESHOLD = 400


def makePloticusPlot(scan, plotFile):
    '''plot scan n from the SPEC scan object'''
    xVec = scan.data[scan.column_first]
    yVec = scan.data[scan.column_last]
    if len(xVec) == 0:
	raise Exception("No data to plot")
    #------------
    # http://ploticus.sourceforge.net/doc/prefab_lines_ex.html
    #------------
    pl = []
    xMin = xMax = xVec[0]
    yMin = yMax = yVec[0]
    for i in range(len(xVec)):
        pl.append("   %s  %s" % (xVec[i], yVec[i]))
	if xVec[i]<xMin: xMin = xVec[i]
	if yVec[i]<yMin: yMin = yVec[i]
	if xVec[i]>xMax: xMax = xVec[i]
	if yVec[i]>yMax: yMax = yVec[i]
    #---- write the ploticus command file
    commandFile = PLOTICUS_COMMAND_FILE
    (os_level_handle, commandFile) = tempfile.mkstemp(dir="/tmp", text=True)
    #print commandFile
    f = open(commandFile, "w")
    f.write("\n".join(pl))
    f.close()
    #---- execute the ploticus command file
    name = "#%d: %s" % (scan.scanNum, scan.scanCmd)
    specFile = scan.specFile
    print "specFile: ", specFile
    title = "%s, %s" % (specFile, scan.date)
    command = PLOTICUS
    command += " -prefab lines"
    command += " data=%s x=1 y=2" % commandFile
    command += " xlbl=\"%s\"" % scan.column_first
    command += " ylbl=\"%s\"" % scan.column_last
    if len(xVec) >= NO_POINTS_THRESHOLD:
        command += " pointsym=\"none\""
    command += " name=\"%s\"" % name
    command += " title=\"%s\"" % title
    command += " -" + PLOT_FORMAT
    command += " -o " + plotFile
    lex = shlex.split(command)
    p = subprocess.Popen(lex)
    p.wait()
    os.remove(commandFile)


def openSpecFile(specFile):
    '''convenience routine so that others do not have to import prjPySpec'''
    sd = prjPySpec.specDataFile(specFile)
    return sd


def findScan(sd, n):
    '''return the first scan with scan number "n" from the spec data file object or None'''
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
