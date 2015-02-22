#!/usr/bin/env python

'''
   read a SPEC data file and plot all the scans

   .. note:: also copies files to USAXS site on XSD WWW server using rsync
'''


import datetime
import logging
import os
import sys
import time
import shutil
import specplot
import localConfig      # definitions for 9-ID
import wwwServerTransfers


SVN_ID = "$Id$"

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
        f = open(cache_file, 'w')
        for key, val in sorted(cache.items()):
            f.write('%s\t%f\n' % (key, val))
        f.close()

    changed = False
    mtime = getTimeFileModified(fname)
    if MTIME_CACHE is None:
        # only read this file once
        MTIME_CACHE = readCacheFile(localConfig.MTIME_CACHE_FILE)

    if (fname in MTIME_CACHE and mtime > MTIME_CACHE[fname]) or fname not in MTIME_CACHE:
        MTIME_CACHE[fname] = mtime
        changed = True
  
    if changed:
        logger('  SPEC data file updated: ' + fname)
        saveCacheFile(localConfig.MTIME_CACHE_FILE, MTIME_CACHE)
      
    return changed


def plotAllSpecFileScans(specFile):
    '''make standard plots for all scans in the specFile'''
    if not os.path.exists(specFile):
        return

    # decide here if SPEC file needs to be opened for possible replot of scan data
    mtime_specFile = getTimeFileModified(specFile)
    png_directory = get_PngDir(specFile)
    if not os.path.exists(png_directory):
        mtime_pngdir = 0
    else:
        mtime_pngdir = getTimeFileModified(png_directory)
    # compare mtime of data file with mtime of PNG directory
    if mtime_pngdir > mtime_specFile or not is_mtime_changed(specFile):
        # do nothing if plot directory was last updated _after_ the specFile
        # This assumes people don't modify the png_directory
        return
    logger('updating plots in directory: ' + png_directory)
    logger('  mtime_specFile: ' + str(mtime_specFile))
    logger('  mtime_pngdir:   ' + str(mtime_pngdir))

    try:
        logger('opening SPEC data file: ' + specFile)
        sd = specplot.openSpecFile(specFile)
    except:
        return    # could not open file, be silent about it
    if len(sd.headers) == 0:    # no scan header found, again, silence
        return

    plotList = []
    newFileList = [] # list of all new files created

    basename = getBaseName(specFile)
    if not os.path.exists(png_directory):
        os.makedirs(png_directory)
        logger('creating directory: ' + png_directory)
        
    # copy the SPEC data file to the WWW site, only if file has newer mtime
    baseSpecFile = os.path.basename(specFile)
    wwwSpecFile = os.path.join(png_directory, baseSpecFile)
    if needToCopySpecDataFile(wwwSpecFile, mtime_specFile):
        # copy specFile to WWW site
        logger('  copying SPEC data file to web directory: ' + wwwSpecFile)
        shutil.copy2(specFile,wwwSpecFile)
        newFileList.append(wwwSpecFile)

    HREF_FORMAT = "<a href=\"%s\">"
    HREF_FORMAT += "<img src=\"%s\" width=\"150\" height=\"75\" alt=\"%s\"/>"
    HREF_FORMAT += "</a>"

    for scan in sd.scans.values():
        basePlotFile = "s%05d.png" % scan.scanNum
        fullPlotFile = os.path.join(png_directory, basePlotFile)
        altText = "#%d: %s" % (scan.scanNum, scan.scanCmd)
        href = HREF_FORMAT % (basePlotFile, basePlotFile, altText)
        plotList.append(href)
        #print "specplot.py %s %d %s" % (specFile, scan.scanNum, fullPlotFile)
        cmd = scan.scanCmd.strip()
        cmd = cmd[:cmd.find(' ')]
        if needToMakePlot(fullPlotFile, mtime_specFile):
            try:
                logger('  creating SPEC data scan image: ' + basePlotFile)
                specplot.makeScanImage(scan, fullPlotFile)
                newFileList.append(fullPlotFile)
            except:
                exc = sys.exc_info()[1]
                msg = "ERROR: '%s' %s #%d" % (exc, specFile, scan.scanNum)
                # print msg
                plotList.pop()     # rewrite the default link
                plotList.append("<!-- " + msg + " -->")
                altText = "%s: #%d %s" % (exc, scan.scanNum, scan.scanCmd)
                href = HREF_FORMAT % (basePlotFile, basePlotFile, altText)
                plotList.append(href)

    htmlFile = os.path.join(png_directory, "index.html")
    if len(newFileList) or not os.path.exists(htmlFile):
        logger('  creating/updating index.html file')
        html = build_index_html(baseSpecFile, specFile, plotList)
        f = open(htmlFile, "w")
        f.write(html)
        f.close()
        newFileList.append(htmlFile)
        
    # touch to update the mtime on the png_directory
    os.utime(png_directory, None)
    
    #------------------
    if len(newFileList):
        cwd = os.getcwd()
        os.chdir(wwwServerTransfers.LOCAL_WWW)
        try:
            logger('  uploading files to WWW server: ' + ', '.join(newFileList))
            upload(newFileList, sd)
        except Exception, exc:
            pass        # TODO: what now?
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
    target = wwwServerTransfers.SERVER_WWW_HOMEDIR + '/' + os.path.join('www', 'livedata')
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
    data_file_root_name = os.path.splitext(os.path.split(specFile)[1])[0]
    date_str = get_SpecFileDate(specFile)
    if date_str is None:
        return
    return getBaseDir(data_file_root_name, date_str)


def get_SpecFileDate(specFile):
    '''return the #D date of the SPEC data file or None'''
    # Get that without parsing the data file, it's on the 3rd line of the file.
    #     #F 06_19_Tony.dat
    #     #E 1403198515
    #     #D Thu Jun 19 12:21:55 2014
    if not os.path.exists(specFile):
        return None

    # read the first lines of the file and validate for SPEC data file format
    f = open(specFile, 'r')
    line = f.readline()
    if not line.startswith('#F '): return None
    line = f.readline()
    if not line.startswith('#E '): return None
    line = f.readline()
    if not line.startswith('#D '): return None
    f.close()

    return line[2:].strip()  # 'Thu Jun 19 12:21:55 2014'


def getBaseDir(basename, date):
    '''find the path based on the date in the spec file'''
    path = localConfig.LOCAL_SPECPLOTS_DIR
    return os.path.join(path, datePath(date), basename)


def getTimeFileModified(file):
    '''@return: time (float) file was last modified'''
    return os.path.getmtime(file)


def needToMakePlot(fullPlotFile, mtime_specFile):
    '''
    Determine if a plot needs to be (re)made
    Use mtime as the basis
    @return: True or False
    '''
    remake_plot = True
    if os.path.exists(fullPlotFile):
        mtime_plotFile = getTimeFileModified(fullPlotFile)
        if mtime_plotFile > mtime_specFile:
            # plot was made after the data file was updated
            remake_plot = False     # don't remake the plot
    # TODO: was the data in _this_ plot changed since the last time the SPEC file was modified?
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
    comment += "   SVN: %s\n"        % SVN_ID
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


def logger(message):
    '''
    log a message or report from this module

    :param str message: words to be logged
    '''
    #print message
    now = datetime.datetime.now()
    name = os.path.basename(sys.argv[0])
    pid = os.getpid()
    text = "(%d,%s,%s) %s" % (pid, name, now, message)
    #print text
    logging.info(text)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filelist = sys.argv[1:]                     # usual command-line use
    else:
        filelist = [localConfig.TEST_SPEC_DATA]     # developer use

    log_file = os.path.join(localConfig.LOCAL_SPECPLOTS_DIR, 'processing.log')
    logging.basicConfig(filename=log_file, level=logging.INFO)
    logger('>'*10 + ' starting')
    logger('file list: ' + ', '.join(filelist))

    for specFile in filelist:
        plotAllSpecFileScans(specFile)
    logger('<'*10 + ' finished')


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
