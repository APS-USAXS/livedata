#!/usr/bin/env python

'''
read a SPEC data file and plot scan n using ploticus

.. note:: does not copy any file to XSD WWW server
'''

import argparse
import numpy
import os
import sys
import tempfile
import time
from spec2nexus import spec             # read SPEC data files
import localConfig                      # definitions for 9-ID
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

        Q = ufs.reduced[s_num_bins]['Q']
        R = ufs.reduced[s_num_bins]['R']
        plotData = zip(Q, R)
    else:
        plotData = []
    return plotData


def process_NexusImageData(scan, imgfile, **attr):
    '''make image from raw NeXus 2-d detector data file'''
    if not os.path.exists(os.path.dirname(imgfile)):
        return

    scanCmd = scan.scanCmd.split()[0]

    path = os.path.dirname(scan.header.parent.fileName)
    # if scanCmd in ('pinSAXS', 'WAXS'):
    #     path += '_' + dict(pinSAXS='saxs', WAXS='waxs')[scanCmd]

    h5file = scan.scanCmd.split()[1]
    if h5file.find('Z:') >= 0:
        # MS Windows file path
        h5file = h5file.replace('Z:', '/data')  # convert mount point to Linux
        h5file = h5file.replace('\\', '/')      # convert delimiters to Linux
    h5file = os.path.abspath( os.path.join(path, h5file) )
    if os.path.exists(h5file) and not os.path.exists(imgfile):
        path = localConfig.HDF5_PATH_TO_IMAGE_DATA
        handle_2d.make_png(h5file, imgfile, path, **attr)
        print 'created: ' + imgfile


def makeScanImage(scan, plotFile):
    '''make an image from the SPEC scan object'''
    scanCmd = scan.scanCmd.split()[0]
    if scanCmd == 'USAXSImaging':
        # make simple image file of the data
        process_NexusImageData(scan, plotFile, log_image=False)
    elif scanCmd == 'pinSAXS':
        # make simple image file of the data
        process_NexusImageData(scan, plotFile)
    elif scanCmd == 'WAXS':
        # make simple image file of the data
        process_NexusImageData(scan, plotFile)
    elif scanCmd == 'FlyScan':
        plotData = retrieve_flyScanData(scan)
        if len(plotData) > 0:
            #ploticus__process_plotData(scan, plotData, plotFile)
            mpl__process_plotData(scan, plotData, plotFile)
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
                #ploticus__process_plotData(scan, plotData, plotFile)
                mpl__process_plotData(scan, plotData, plotFile)


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


def mpl__process_plotData(scan, plotData, plotFile):
    '''make MatPlotLib line chart image from raw SPEC or FlyScan data'''
    import plot_mpl
    x, y = zip(*plotData)
    scan_macro = scan.scanCmd.split()[0]
    if scan_macro in ('uascan', 'sbuascan'):
        xlog = False
        ylog = True
    elif scan_macro in ('FlyScan', ):
        xlog = True
        ylog = True
    else:
        xlog = False
        ylog = False
    title = scan.specFile
    subtitle = "#%d: %s" % (scan.scanNum, scan.scanCmd)
    plot_mpl.spec_plot(x, y, 
                       plotFile, 
                       title=title, 
                       subtitle=subtitle, 
                       xtitle=scan.column_first, 
                       ytitle=scan.column_last, 
                       xlog=xlog, ylog=ylog)


def ploticus__process_plotData(scan, plotData, plotFile):
    '''make Ploticus line chart image from raw SPEC or FlyScan data'''
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
    convenience routine so that others do not have to import spec2nexus.spec
    '''
    sd = spec.SpecDataFile(specFile)
    return sd


def findScan(sd, n):
    '''
    return the first scan with scan number "n"
    from the spec data file object or None
    '''
    scan = sd.getScan(int(n))
    return scan


def main():
    doc = __doc__.strip().splitlines()[0]
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('specFile',    help="SPEC data file name")
    parser.add_argument('scan_number', help="scan number in SPEC file", type=int)
    parser.add_argument('plotFile',    help="output plot file name")
    results = parser.parse_args()

    specData = openSpecFile(results.specFile)
    scan = findScan(specData, results.scan_number)
    makeScanImage(scan, results.plotFile)


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
