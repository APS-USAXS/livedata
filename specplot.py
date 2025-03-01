#!/usr/bin/env python

'''
read a SPEC data file and plot scan n

.. note:: does not copy any file to XSD WWW server
'''

import argparse
import logging
import os
from spec2nexus import spec             # read SPEC data files

import localConfig                      # definitions for 9-ID
import reduceFlyData
import handle_2d


logger = logging.getLogger(__name__)

def retrieve_specScanData(scan):
    '''retrieve default data from spec data file'''
    x = scan.data[scan.column_first]
    y = scan.data[scan.column_last]
    return (x, y)


def retrieve_flyScanData(scan):
    '''retrieve reduced, rebinned data from USAXS Fly Scans'''
    if hasattr(scan, "MD") and scan.MD.get("hdf5_path") is not None:
        # Bluesky wrote this SPEC data file
        path = scan.MD.get("hdf5_path")
        hdf_file_name = scan.MD.get("hdf5_file")
    else:
        # SPEC wrote this data file
        key_string = 'FlyScan file name = '
        hdf_file_name = ""  # in case key_string is not found
        for comment in scan.comments:
            if key_string in comment:
                index = comment.find(key_string) + len(key_string)
                path = os.path.dirname(scan.header.parent.fileName)
                hdf_file_name = comment[index:-1]
                break
    abs_file = os.path.abspath(os.path.join(path, hdf_file_name))
    if os.path.exists(abs_file):
        s_num_bins = str(localConfig.REDUCED_FLY_SCAN_BINS)
        ufs = reduceFlyData.UsaxsFlyScan(abs_file)
        ufs.read_reduced()

        needs_calc = dict(full = not ufs.has_reduced('full'))
        needs_calc[s_num_bins] = not ufs.has_reduced(s_num_bins)
        if needs_calc['full']:
            #ufs.make_archive()
            ufs.reduce()
            ufs.save(abs_file, 'full')
            needs_calc[s_num_bins] = True
        if needs_calc[s_num_bins]:
            ufs.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
            ufs.save(abs_file, s_num_bins)

        Q = ufs.reduced[s_num_bins]['Q']
        R = ufs.reduced[s_num_bins]['R']
        plotData = (Q, R)
    else:
        plotData = []
    return plotData


def process_NexusImageData(scan, imgfile, **attr):
    '''make image from raw NeXus 2-d detector data file'''
    if not os.path.exists(os.path.dirname(imgfile)):
        return

    if hasattr(scan, "MD") and scan.MD.get("hdf5_path") is not None:
        # Bluesky wrote this SPEC data file
        path = scan.MD.get("hdf5_path")
        h5file = scan.MD.get("hdf5_file")
    else:
        # SPEC wrote this data file
        path = os.path.dirname(scan.header.parent.fileName)
        h5file = scan.scanCmd.split()[1]

    if h5file.find('Z:') >= 0:
        # MS Windows file path
        h5file = h5file.replace('Z:', '/data')  # convert mount point to Linux
        h5file = h5file.replace('\\', '/')      # convert delimiters to Linux

    h5file = os.path.abspath( os.path.join(path, h5file) )

    # TODO: common user problem happens here
    # the file name is specified in the SPEC file
    # often, the file extension used by area detector
    # is different than the SPEC file and "file not found" happens
    # Could by more flexible by searching other possible extensions if first file is not found.

    if os.path.exists(h5file) and not os.path.exists(imgfile):
        path = localConfig.HDF5_PATH_TO_IMAGE_DATA
        handle_2d.make_png(h5file, imgfile, path, **attr)
        logger.info('created: ' + imgfile)


def makeScanImage(scan, plotFile):
    '''make an image from the SPEC scan object'''
    scanCmd = scan.scanCmd.split()[0]
    if scanCmd == 'USAXSImaging':
        # make simple image file of the data
        # removed: https://github.com/APS-USAXS/livedata/issues/1
        # process_NexusImageData(scan, plotFile, log_image=False)
        pass
    elif scanCmd in ('pinSAXS', 'SAXS', 'WAXS') or scanCmd.startswith("SAXS(") or scanCmd.startswith("WAXS("):
        # make simple image file of the data
        process_NexusImageData(scan, plotFile)
    elif scanCmd in ('FlyScan', 'sbFlyScan') or scanCmd.lower().startswith("flyscan("):
        plotData = retrieve_flyScanData(scan)
        if len(plotData) > 0:
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
                mpl__process_plotData(scan, plotData, plotFile)


def mpl__process_plotData(scan, plotData, plotFile):
    '''make MatPlotLib line chart image from raw SPEC or FlyScan data'''
    import plot_mpl
    x, y = plotData
    scan_macro = scan.scanCmd.split()[0]
    if scan_macro in ('uascan', 'sbuascan'):
        xlog = False
        ylog = True
        xtitle = scan.column_first
        ytitle = scan.column_last
    elif scan_macro in ('FlyScan', 'sbFlyScan', ) or scan_macro.lower().startswith("flyscan("):
        xlog = True
        ylog = True
        xtitle = r'$|\vec{Q}|, 1/\AA$'
        ytitle = r'USAXS $R(|\vec{Q}|)$, a.u.'
    else:
        xlog = False
        ylog = False
        xtitle = scan.column_first
        ytitle = scan.column_last
    title = scan.specFile
    subtitle = "#%s: %s" % (scan.scanNum, scan.scanCmd)
    #timestamp_str = scan.date                REMOVE ME
    plot_mpl.spec_plot(x, y,  plotFile,
                       title=title,  subtitle=subtitle,
                       xtitle=xtitle,  ytitle=ytitle,
                       xlog=xlog, ylog=ylog,
                       timestamp_str=scan.date)


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
    scan = sd.getScan(str(n))
    return scan


def main():
    doc = __doc__.strip().splitlines()[0]
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('specFile',    help="SPEC data file name")
    parser.add_argument('scan_number', help="scan number in SPEC file", type=str)
    parser.add_argument('plotFile',    help="output plot file name")
    results = parser.parse_args()

    specData = openSpecFile(results.specFile)
    scan = findScan(specData, results.scan_number)
    # scan.interpret()
    makeScanImage(scan, results.plotFile)


if __name__ == '__main__':
    main()
