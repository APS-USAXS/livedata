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
   @note: does not copy any file to XSD WWW server
'''

import os
import os.path
import sys
import tempfile
import prjPySpec        # read SPEC data files
import localConfig      # definitions for 15ID
import wwwServerTransfers

def makePloticusPlot(scan, plotFile):
    '''plot scan n from the SPEC scan object'''
    plotData = zip(scan.data[scan.column_first], scan.data[scan.column_last])
    if len(plotData) == 0:
        raise Exception("No data to plot")
    #------------
    # http://ploticus.sourceforge.net/doc/prefab_lines_ex.html
    #------------
    pl = format_ploticus_data(plotData)
    dataFile = write_ploticus_data_file(pl['data'])

    #---- execute the ploticus command file using a "prefab" plot style
    run_ploticus_command_script(scan, dataFile, plotData, plotFile)


def write_ploticus_data_file(data):
    '''
    find x & y min & max
    @return: dictionary
    '''
    #---- write the ploticus data file
    ext = os.extsep + "pl"
    (f, dataFile) = tempfile.mkstemp(dir="/tmp", text=True, suffix=ext)
    f = open(dataFile, "w")
    f.write("\n".join(data))
    f.close()
    return dataFile


def format_ploticus_data(data):
    '''
    find x & y min & max
    @return: dictionary
    '''
    pl = []
    xMin = xMax = yMin = yMax = None
    for (x, y) in data:
        pl.append("   %s  %s" % (x, y))
        if xMin == None:
            xMin = xMax = x
            yMin = yMax = y
        else:
            if x < xMin: xMin = x
            if y < yMin: yMin = y
            if x > xMax: xMax = x
            if y > yMax: yMax = y
    dict = {
            'data': pl,
            'xMin': xMin,
            'xMax': xMax,
            'yMin': yMin,
            'yMax': yMax
            }
    return dict


def run_ploticus_command_script(scan, dataFile, plotData, plotFile):
    '''
    execute the ploticus command file using a "prefab" plot style
    '''
    # ploticus needs this
    os.environ['PLOTICUS_PREFABS'] = localConfig.PLOTICUS_PREFABS
    
    name = "#%d: %s" % (scan.scanNum, scan.scanCmd)
    title = "%s, %s" % (scan.specFile, scan.date)
    command = localConfig.PLOTICUS
    command += " -prefab lines"
    command += " data=%s x=1 y=2" % dataFile
    command += " xlbl=\"%s\"" % scan.column_first
    command += " ylbl=\"%s\"" % scan.column_last
    if len(plotData) >= localConfig.LINE_ONLY_THRESHOLD:
        command += " pointsym=\"none\""
    command += " name=\"%s\"" % name
    command += " title=\"%s\"" % title
    command += " -" + localConfig.PLOT_FORMAT
    command += " -o " + plotFile

    wwwServerTransfers.execute_command(command)
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


def makePloticusPlotByScanNum(specFile, scan_number, plotFile):
    '''
    all-in-one function
    '''
    specData = openSpecFile(specFile)
    scan = findScan(specData, scan_number)
    makePloticusPlot(scan, plotFile)


if __name__ == '__main__':
    specFile = localConfig.TEST_SPEC_DATA
    scan_number = localConfig.TEST_SPEC_SCAN_NUMBER
    plotFile = localConfig.TEST_PLOTFILE
    if len(sys.argv) == 4:
        (specFile, scan_number, plotFile) = sys.argv[1:4]
    else:
        print "usage: %s specFile scan_number plotFile" % sys.argv[0]
        sys.exit()
    try:
        makePloticusPlotByScanNum(specFile, scan_number, plotFile)
    except:
        pass