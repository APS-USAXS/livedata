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

.. note:: does not copy any file to XSD WWW server
'''

import numpy
import os
import sys
import tempfile
import time
from spec2nexus import prjPySpec        # read SPEC data files
import localConfig                      # definitions for 15ID
import wwwServerTransfers
import reduceFlyData
import handle_2d


def retrieve_specScanData(scan):
    '''retrieve default data from spec data file'''
    x = scan.data[scan.column_first]
    y = scan.data[scan.column_last]
    return zip(x, y)


def retrieve_flyScanData(scan):
    '''retrieve reduced, rebinned data from USAXS Fly Scans'''
    path = os.path.dirname(scan.header.parent.fileName)
    #hdf_file_name = scan.comments[2].split()[-1].rstrip('.')    # fails if file name has spaces (should not have these)
    key_string = 'FlyScan file name = '
    comment = scan.comments[2]
    index = comment.find(key_string) + len(key_string)
    hdf_file_name = comment[index:-1]
    abs_file = os.path.abspath(os.path.join(path, hdf_file_name))
    if os.path.exists(abs_file):
        s_num_bins = str(localConfig.REDUCED_FLY_SCAN_BINS)
        ufs = reduceFlyData.UsaxsFlyScan(abs_file)
        ufs.read_reduced()

        needs_calc = dict(full = not ufs.has_reduced('full'))
        needs_calc[s_num_bins] = not ufs.has_reduced(s_num_bins)
        if needs_calc['full']:
            ufs.make_archive()
            ufs.reduce()
            ufs.save(abs_file, 'full')
            needs_calc[s_num_bins] = True
        if needs_calc[s_num_bins]:
            ufs.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
            ufs.save(abs_file, s_num_bins)

        # USAXS Fly Scan plots will be ln(R) v. ln(Q), otherwise useless
        Q = numpy.log(ufs.reduced[s_num_bins]['Q'])
        R = numpy.log(ufs.reduced[s_num_bins]['R'])
        plotData = zip(Q, R)
    else:
        plotData = []
    return plotData


def process_NexusImageData(scan, imgfile):
    '''make image from raw NeXus 2-d detector data file'''
    scanCmd = scan.scanCmd.split()[0]
    h5file = os.path.split( scan.scanCmd.split()[1] )[1]
    path = os.path.splitext(scan.header.parent.fileName)[0]
    path += '_' + dict(pinSAXS='saxs', WAXS='waxs')[scanCmd]

    if not os.path.exists(path):
        return
    h5file = os.path.abspath( os.path.join(path, h5file) )
    if not os.path.exists(h5file):
        return
    if not os.path.exists(os.path.split(imgfile)[0]):
        return

    if not os.path.exists(imgfile):
        handle_2d.make_png(h5file, imgfile, localConfig.HDF5_PATH_TO_IMAGE_DATA)
        print 'created: ' + imgfile


def makeScanImage(scan, plotFile):
    '''make an image from the SPEC scan object'''
    scanCmd = scan.scanCmd.split()[0]
    if scanCmd == 'pinSAXS':
        # make simple image file of the data
        process_NexusImageData(scan, plotFile)
    elif scanCmd == 'WAXS':
        # make simple image file of the data
        process_NexusImageData(scan, plotFile)
    elif scanCmd == 'FlyScan':
        plotData = retrieve_flyScanData(scan)
        if len(plotData) > 0:
            ploticus__process_plotData(scan, plotData, plotFile)
    else:
        # plot last column v. first column
        plotData = retrieve_specScanData(scan)
        if len(plotData) > 0:
            # only proceed if mtime of SPEC data file is newer than plotFile
            mtime_sdf = os.path.getmtime(scan.header.parent.fileName)
            if os.path.exists(plotFile):
                mtime_pf = os.path.getmtime(plotFile)
            else:
                mtime_pf = 0
            if mtime_sdf > mtime_pf:
                # TODO: check if this scan _needs_ to be updated
                ploticus__process_plotData(scan, plotData, plotFile)


def write_file_by_lines(data):
    '''
    write data to a text file
    
    :param [str]: data (list of lines for the file)
    '''
    #---- write the ploticus data file
    ext = os.extsep + "pl"
    (_, dataFile) = tempfile.mkstemp(dir="/tmp", text=True, suffix=ext)
    f = open(dataFile, "w")
    f.write("\n".join(data))
    f.close()
    return dataFile


def ploticus__process_plotData(scan, plotData, plotFile):
    '''make line chart image from raw SPEC or FlyScan data'''
    # see: http://ploticus.sourceforge.net/doc/prefab_lines_ex.html
    
    # format the x&y data as ploticus text
    if len(plotData) == 0:
        pl_lines = ["   %s  %s" % (0, 0),]
    else:
        pl_lines = ["   %s  %s" % (x, y) for (x, y) in plotData]
    #     # also find x & y min & max
    #     x, y = zip(*plotData)
    #     pl = dict(data=pl_lines, xMin=min(x), xMax=max(x), yMin=min(y), yMax=max(y))
    dataFile = write_file_by_lines(pl_lines)

    #---- execute the ploticus command file using a "prefab" plot style
    # ploticus needs this
    os.environ['PLOTICUS_PREFABS'] = localConfig.PLOTICUS_PREFABS
    
    name = "#%d: %s" % (scan.scanNum, scan.scanCmd)
    if len(plotData) == 0:
        name += ' (no data to plot)'
    try:
        specFileName = scan.specFile
    except AttributeError:
        # was in scan.specFile but interface changed
        specFileName = 'USAXS FlyScan %d' % scan.scanNum
    title = "%s, %s" % (specFileName, scan.date)
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
    print 'created: ' + plotFile


def openSpecFile(specFile):
    '''
    convenience routine so that others do not have to import prjPySpec
    '''
    sd = prjPySpec.SpecDataFile(specFile)
    return sd


def findScan(sd, n):
    '''
    return the first scan with scan number "n"
    from the spec data file object or None
    '''
    scan = sd.getScan(int(n))
    return scan


def main():
    specFile = localConfig.TEST_SPEC_DATA
    scan_number = localConfig.TEST_SPEC_SCAN_NUMBER
    plotFile = localConfig.TEST_PLOTFILE
    if len(sys.argv) == 4:
        (specFile, scan_number, plotFile) = sys.argv[1:4]
    else:
        print "usage: %s specFile scan_number plotFile" % sys.argv[0]
        sys.exit()
    try:
        specData = openSpecFile(specFile)
        scan = findScan(specData, scan_number)
        makeScanImage(scan, plotFile)
    except:
        pass


if __name__ == '__main__':
    # sys.argv = sys.argv[0:]
    # sys.argv.append('testdata/2014-04/04_14_Winans.dat')
    # sys.argv.append('/data/USAXS_data/2014-06/06_16_NXSchool.dat')
    # sys.argv.append(str(133))
    # sys.argv.append('/tmp/specplot.png')
    main()
