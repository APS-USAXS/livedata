#!/usr/bin/env python

'''
   read a SPEC data file and plot all the scans

   .. note:: also copies files to USAXS site on XSD WWW server using rsync
'''


import logging
import os
os.environ['HDF5_DISABLE_VERSION_CHECK'] = '2'
import shutil
import spec2nexus
import sys
import time

logger = logging.getLogger(__name__)

try:
    # better reporting of SEGFAULT
    # http://faulthandler.readthedocs.org
    import faulthandler
    faulthandler.enable()
    logger.info("faulthandler: module enabled")
except ImportError, exc:
    logger.warning("faulthandler: module not imported")

import specplot
import localConfig      # definitions for 9-ID
import wwwServerTransfers


MTIME_CACHE = None

def is_mtime_changed(fname):
    '''
    compare the file modified time of fname with a file cache

    This is used to avoid redundant scanning of data files when no new data is available.
    The fname file has already been verified to exist.
    '''
    global MTIME_CACHE

    def readCacheFile(cache_file):
        cache = {}
        if os.path.exists(cache_file):
            for line in open(cache_file, 'r').readlines():
                key = line.split('\t')[0]
                val = float(line.strip().split('\t')[1])
                cache[key] = val
        return cache

    def saveCacheFile(cache_file, cache):
        with open(cache_file, 'w') as f:
            for key, val in sorted(cache.items()):
                f.write('%s\t%f\n' % (key, val))

    changed = False
    mtime = getTimeFileModified(fname)
    if MTIME_CACHE is None:
        # only read this file once
        MTIME_CACHE = readCacheFile(localConfig.MTIME_CACHE_FILE)

    if (fname in MTIME_CACHE and mtime > MTIME_CACHE[fname]) or fname not in MTIME_CACHE:
        MTIME_CACHE[fname] = mtime
        changed = True

    if changed:
        logger.info('  SPEC data file updated: ' + fname)
        saveCacheFile(localConfig.MTIME_CACHE_FILE, MTIME_CACHE)

    return changed


def plotAllSpecFileScans(specFile):
    '''make standard plots for all scans in the specFile'''
    if not os.path.exists(specFile):
        return

    # decide here if SPEC file needs to be opened for possible replot of scan data
    mtime_specFile = getTimeFileModified(specFile)
    png_directory = get_PngDir(specFile)
    if png_directory is None or not os.path.exists(png_directory):
        mtime_pngdir = 0
    else:
        mtime_pngdir = getTimeFileModified(png_directory)
    # compare mtime of data file with mtime of PNG directory
    if mtime_pngdir > mtime_specFile or not is_mtime_changed(specFile):
        # do nothing if plot directory was last updated _after_ the specFile
        # This assumes people don't modify the png_directory
        return
    if png_directory != None:
        logger.info('updating plots in directory: ' + png_directory)
    else:
        logger.info('updating plots in directory: None')
    logger.info('  mtime_specFile: ' + str(mtime_specFile))
    logger.info('  mtime_pngdir:   ' + str(mtime_pngdir))

    try:
        logger.info('opening SPEC data file: ' + specFile)
        # sd = specplot.openSpecFile(specFile)
        sd = spec2nexus.spec.SpecDataFile(specFile)
    except Exception:
        return    # could not open file, be silent about it
    if len(sd.headers) == 0:    # no scan header found, again, silence
        return

    plotList = []
    newFileList = [] # list of all new files created

    if not os.path.exists(png_directory):
        os.makedirs(png_directory)
        logger.info('creating directory: ' + png_directory)

    # copy the SPEC data file to the WWW site, only if file has newer mtime
    baseSpecFile = os.path.basename(specFile)
    wwwSpecFile = os.path.join(png_directory, baseSpecFile)

    HREF_FORMAT = "<a href=\"%s\">"
    HREF_FORMAT += "<img src=\"%s\" width=\"150\" height=\"75\" alt=\"%s\"/>"
    HREF_FORMAT += "</a>"

    try:
        scan_number_list = sd.getScanNumbers()
    except ValueError as exc:
        # 2018-11-12, prj:
        # bypass a problem referencing non-integer scan numbers:
        # see: https://github.com/APS-USAXS/ipython-usaxs/issues/76
        scan_number_list = []
        logger.warn("non-integer scan number in " + specFile)
        logger.warn("traceback:\n" + str(exc))

    for scan_number in scan_number_list:
        # TODO: was the data in _this_ scan changed since the last time the SPEC file was modified?
        #  Check the scan's date/time stamp and also if the plot exists.
        #  For a scan N, the plot may exist if the scan was in progress at the last update.
        #  For sure, if a plot for N+1 exists, no need to remake plot for scan N.  Thus:
        #    Always remake if plot for scan N+1 does not exist
        scan = sd.getScan(scan_number)
        scan.interpret()
        basePlotFile = "s%s.png" % scan.scanNum
        fullPlotFile = os.path.join(png_directory, basePlotFile)
        altText = "#%s: %s" % (scan.scanNum, scan.scanCmd)
        href = HREF_FORMAT % (basePlotFile, basePlotFile, altText)
        plotList.append(href)
        logger.debug("{} {} {}".format(specFile, scan.scanNum, fullPlotFile))
        # cmd = scan.scanCmd.strip().split()[0]
        if needToMakePlot(fullPlotFile, mtime_specFile):
            try:
                logger.info('  creating SPEC data scan image: ' + basePlotFile)
                specplot.makeScanImage(scan, fullPlotFile)
                newFileList.append(fullPlotFile)
            except Exception as _exc:
                msg = "ERROR: '%s' %s #%s" % (_exc.message, specFile, scan.scanNum)
                logger.debug(msg)
                plotList.pop()     # rewrite the default link
                plotList.append("<!-- " + msg + " -->")
                altText = "%s: #%s %s" % (_exc.message, scan.scanNum, scan.scanCmd)
                href = HREF_FORMAT % (basePlotFile, basePlotFile, altText)
                plotList.append(href)

    htmlFile = os.path.join(png_directory, "index.html")
    if len(newFileList) or not os.path.exists(htmlFile):
        logger.info('  creating/updating index.html file')
        html = build_index_html(baseSpecFile, specFile, plotList)
        with open(htmlFile, "w") as f:
            f.write(html)
        newFileList.append(htmlFile)

    # touch to update the mtime on the png_directory
    os.utime(png_directory, None)

    if needToCopySpecDataFile(wwwSpecFile, mtime_specFile):
        # copy specFile to WWW site
        logger.info('  copying SPEC data file to web directory: ' + wwwSpecFile)
        shutil.copy2(specFile,wwwSpecFile)
        newFileList.append(wwwSpecFile)

    #------------------
    if len(newFileList):
        cwd = os.getcwd()
        os.chdir(wwwServerTransfers.LOCAL_WWW)
        try:
            logger.info('  uploading files to WWW server: ' + ', '.join(newFileList))
            upload(newFileList, sd)
        except Exception, exc:
            logger.error('  ERROR %s: could not upload to WWW server' % exc.message)
        os.chdir(cwd)


def upload(newFileList, sdf):
    '''
    upload the list of files to the XSD WWW server

    limit the rsync to just the specplots/yyyymm subdir

    :param [str] newFileList: list of local files (absolute path reference) to be uploaded
    :param obj sdf: instance of SpecDataFile
    '''
    yyyymm = datePath(sdf.headers[-1].date)
    source = os.path.join('specplots', yyyymm + '/')
    target = wwwServerTransfers.SERVER_WWW_LIVEDATA
    command = wwwServerTransfers.RSYNC
    command += " -rRtz %s %s" % (source, target)
    wwwServerTransfers.execute_command(command)


def getBaseName(specFile):
    '''get the base plot name from the spec file name (no path or extension)'''
    return os.path.splitext(os.path.basename(specFile))[0]


def datePath(date):
    '''convert the date into a path: yyyy/mm'''
    dateStr = time.strptime(date, "%a %b %d %H:%M:%S %Y")
    yyyy = "%04d" % dateStr.tm_year
    mm = "%02d" % dateStr.tm_mon
    return os.path.join(yyyy, mm)


def get_PngDir(specFile):
    '''return the PNG directory based on the specFile'''
    basename = os.path.splitext(os.path.basename(specFile))[0]
    date_str = get_SpecFileDate(specFile)
    if date_str is None:
        return
    return getBaseDir(basename, date_str)


def get_SpecFileDate(specFile):
    '''return the #D date of the SPEC data file or None'''
    # Get that without parsing the data file, it's on the 3rd line of the file.
    #     #F 06_19_Tony.dat
    #     #E 1403198515
    #     #D Thu Jun 19 12:21:55 2014
    if not os.path.exists(specFile):
        return None

    # read the first lines of the file and validate for SPEC data file format
    with open(specFile, 'r') as f:
        line = f.readline()
        if not line.startswith('#F '): return None
        line = f.readline()
        if not line.startswith('#E '): return None
        line = f.readline()
        if not line.startswith('#D '): return None

    return line[2:].strip()  # 'Thu Jun 19 12:21:55 2014'


def getBaseDir(basename, date):
    '''find the path based on the date in the spec file'''
    path = localConfig.LOCAL_SPECPLOTS_DIR
    return os.path.join(path, datePath(date), basename)


def getTimeFileModified(filename):
    '''@return: time (float) filename was last modified'''
    return os.path.getmtime(filename)


def needToMakePlot(fullPlotFile, mtime_specFile):
    '''
    Determine if a plot needs to be (re)made.  Use mtime as the basis.

    @return: True or False
    '''
    remake_plot = True
    if os.path.exists(fullPlotFile):
        mtime_plotFile = getTimeFileModified(fullPlotFile)
        if mtime_plotFile > mtime_specFile:
            # plot was made after the data file was updated
            remake_plot = False     # don't remake the plot
    return remake_plot


def needToCopySpecDataFile(wwwSpecFile, mtime_specFile):
    '''
    Determine if spec data file needs to be copied
    Base the decision on the mtime (last modification time of the file)
    @return: True or False
    '''
    copySpecFile = False
    if os.path.exists(wwwSpecFile):
        mtime_wwwSpecFile = getTimeFileModified(wwwSpecFile)
        if mtime_specFile > mtime_wwwSpecFile:
            copySpecFile = True     # specFile is newer, copy to WWW site
    else:
        copySpecFile = True     # specFile is not yet on WWW site
    return copySpecFile


def timestamp():
    '''current time as yyyy-mm-dd hh:mm:ss'''
    return time.strftime(
                      localConfig.TIMESTAMP_FORMAT,
                      time.localtime(time.time()))


def build_index_html(baseSpecFile, specFile, plotList):
    '''build index.html content'''
    comment = "\n"
    comment += "   written by: %s\n" % sys.argv[0]
    comment += "   date: %s\n"       % timestamp()
    comment += "\n"
    href = "<a href='%s'>%s</a>" % (baseSpecFile, specFile)
    html  = "<html>\n"
    html += "  <head>\n"
    html += "    <title>SPEC scans from %s</title>\n" % specFile
    html += "    <!-- %s -->\n"                       % comment
    html += "  </head>\n"
    html += "  <body>\n"
    html += "    <h1>SPEC scans from: %s</h1>\n"      % specFile
    html += "\n"
    html += "    spec file: %s\n"                     % href
    html += "    <br />\n"
    html += "\n"
    html += "\n"
    html += "\n".join(plotList)
    html += "\n"
    html += "\n"
    html += "  </body>\n"
    html += "</html>\n"
    return html


def main():
    if len(sys.argv) > 1:
        filelist = sys.argv[1:]                     # usual command-line use
    else:
        filelist = [localConfig.TEST_SPEC_DATA]     # developer use

    log_file = os.path.join(localConfig.LOCAL_SPECPLOTS_DIR, 'processing.log')
    log_format = "%(asctime)s (%(levelname)s,%(process)d,%(name)s,%(module)s,%(lineno)d) %(message)s"
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)
    logger = logging.getLogger(__name__)
    logger.info('>'*10 + ' starting')
    logger.info('file list: ' + ', '.join(filelist))

    for specFile in filelist:
        plotAllSpecFileScans(specFile)
    logger.info('<'*10 + ' finished')


if __name__ == '__main__':
    main()
