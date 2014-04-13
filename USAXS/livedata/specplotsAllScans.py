#!/usr/bin/env python

'''
   read a SPEC data file and plot all the scans

   .. note:: also copies files to USAXS site on XSD WWW server using rsync
'''

import os
import sys
import time
import shutil
import specplot
import localConfig      # definitions for 15ID
import wwwServerTransfers


SVN_ID = "$Id$"


def plotAllSpecFileScans(specFile):
    '''make standard plots for all scans in the specFile'''
    if not os.path.exists(specFile):
        return

    try:
        sd = specplot.openSpecFile(specFile)
    except:
        return    # could not open file, be silent about it
    if len(sd.headers) == 0:    # no scan header found, again, silence
        return

    plotList = []
    newFileList = [] # list of all new files created

    mtime_specFile = getTimeFileModified(specFile)
    basename = getBaseName(specFile)
    basedir = getBaseDir(basename, sd.headers[-1].date)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
        
    # copy the SPEC data file to the WWW site, only if file has newer mtime
    baseSpecFile = os.path.basename(specFile)
    wwwSpecFile = os.path.join(basedir, baseSpecFile)
    if needToCopySpecDataFile(wwwSpecFile, mtime_specFile):
        # copy specFile to WWW site
        shutil.copy2(specFile,wwwSpecFile)
        newFileList.append(wwwSpecFile)

    HREF_FORMAT = "<a href=\"%s\">"
    HREF_FORMAT += "<img src=\"%s\" width=\"150\" height=\"75\" alt=\"%s\"/>"
    HREF_FORMAT += "</a>"

    for scan in sd.scans.values():
        basePlotFile = "s%05d.png" % scan.scanNum
        fullPlotFile = os.path.join(basedir, basePlotFile)
        altText = "#%d: %s" % (scan.scanNum, scan.scanCmd)
        href = HREF_FORMAT % (basePlotFile, basePlotFile, altText)
        plotList.append(href)
        #print "specplot.py %s %d %s" % (specFile, scan.scanNum, fullPlotFile)
        cmd = scan.scanCmd.strip()
        cmd = cmd[:cmd.find(' ')]
        ignore_this_scan = cmd in ('pinSAXS', 'WAXS')
        if needToMakePlot(fullPlotFile, mtime_specFile) and not ignore_this_scan:
            try:
                specplot.makePloticusPlot(scan, fullPlotFile)
                newFileList.append(fullPlotFile)
            except:
                exc_value = sys.exc_info()[1]
                msg = "ERROR: '%s' %s #%d" % (exc_value, 
                        specFile, scan.scanNum)
                # print msg
                plotList.pop()     # rewrite the default link
                plotList.append("<!-- " + msg + " -->")
                altText = "%s: #%d %s" % (exc_value, 
                        scan.scanNum, scan.scanCmd)
                href = HREF_FORMAT % (basePlotFile, basePlotFile, altText)
                plotList.append(href)

    htmlFile = os.path.join(basedir, "index.html")
    if len(newFileList) or not os.path.exists(htmlFile):
        html = build_index_html(baseSpecFile, specFile, plotList)
        f = open(htmlFile, "w")
        f.write(html)
        f.close()
        newFileList.append(htmlFile)
        
    #------------------
    if len(newFileList):
        # use rsync to update the XSD WWW server
        # limit the rsync to just the specplots/yyyymm subdir
        yyyymm = datePath(sd.headers[-1].date)
        source = "./www/livedata/specplots" + "/" + yyyymm + "/"
        target = wwwServerTransfers.SERVER_WWW_HOMEDIR
        command = wwwServerTransfers.RSYNC
        command += " -rRtz %s %s" % (source, target)
        wwwServerTransfers.execute_command(command)


def getBaseName(specFile):
    '''get the base plot name from the spec file name (no path or extension)'''
    return os.path.splitext(os.path.basename(specFile))[0]


def datePath(date):
    '''convert the date into a path: yyyy/mm'''
    dateStr = time.strptime(date, "%a %b %d %H:%M:%S %Y")
    yyyy = "%04d" % dateStr[0]
    mm = "%02d" % dateStr[1]
    dd = "%02d" % dateStr[2]
    return os.path.join(yyyy, mm)


def getBaseDir(basename, date):
    '''find the path based on the date in the spec file'''
    firstDir = localConfig.LOCAL_SPECPLOTS_DIR
    return os.path.join(firstDir, datePath(date), basename)


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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filelist = sys.argv[1:]                     # usual command-line use
    else:
        filelist = [localConfig.TEST_SPEC_DATA]     # developer use
    for specFile in filelist:
        plotAllSpecFileScans(specFile)


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
