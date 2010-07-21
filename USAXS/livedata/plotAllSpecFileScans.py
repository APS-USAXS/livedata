#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   read a SPEC data file and plot all the scans
   @TODO: check for 15ID-D readiness
'''

import os
import sys
import time
import shutil
import specplot

TEST_FILE = "/data/USAXS_data/2010-03/03_27.dat"
PLOT_DIR = os.path.join(".", "www", "scanplots")
SPEC_FILE = os.path.join(TEST_FILE.split("/"))
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
SVN_ID = "$Id$"
HREF_FORMAT = "<a href=\"%s\"><img src=\"%s\" width=\"%s\" height=\"%s\" alt=\"%s\"/></a>"
HTML_FORMAT = """<html>
  <head>
    <title>SPEC scans from %s</title>
    <!-- %s -->
  </head>
  <body>
    <h1>SPEC scans from: %s</h1>

      spec file: <a href='%s'>%s</a>
      <br />

%s

  </body>
</html>"""


def plotAllSpecFileScans(specFile):
    '''show the commands to be used'''
    if not os.path.exists(specFile):
        return
    sd = specplot.openSpecFile(specFile)
    if len(sd.headers) == 0:    # no scan header found
        return
    specFile_mtime = os.path.getmtime(specFile)
    basename = os.path.splitext(os.path.basename(specFile))[0]
    date = time.strptime(sd.headers[-1].date, "%a %b %d %H:%M:%S %Y")
    yyyy = "%04d" % date[0]
    mm = "%02d" % date[1]
    dd = "%02d" % date[2]
    basedir = os.path.join(PLOT_DIR, yyyy, mm, dd, basename)
    # shorter path if we cut out the dd part
    basedir = os.path.join(PLOT_DIR, yyyy, mm, basename)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    plotList = []
    for scan in sd.scans:
        basePlotFile = "s%05d.png" % scan.scanNum
        fullPlotFile = os.path.join(basedir, basePlotFile)
        altText = "#%d: %s" % (scan.scanNum, scan.scanCmd)
        plotList.append(HREF_FORMAT % (basePlotFile, basePlotFile, "150", "75", altText))
        #print "specplot.py %s %d %s" % (specFile, scan.scanNum, fullPlotFile)
        remake_plot = True
        if os.path.exists(fullPlotFile):
            plotFile_mtime = os.path.getmtime(fullPlotFile)
            if plotFile_mtime > specFile_mtime:
                # plot was made after the data file was updated, don't remake the plot
                remake_plot = False
        #remake_plot = True  # force new plots for development
        if remake_plot:
            try:
                specplot.makePloticusPlot(scan, fullPlotFile)
            except:
                msg = "ERROR: '%s' %s #%d" % (sys.exc_value, specFile, scan.scanNum)
                print msg
                plotList.pop()     # replace the default link
                plotList.append("<!-- " + msg + " -->")
                altText = "%s: #%d %s" % (sys.exc_value, scan.scanNum, scan.scanCmd)
                plotList.append(HREF_FORMAT % (basePlotFile, basePlotFile, "150", "75", altText))
    baseSpecFile = os.path.basename(specFile)
    datestamp = time.strftime(TIMESTAMP_FORMAT, time.localtime(time.time()))
    commentFormat = """
       written by: %s
       SVN: %s
       date: %s
    """
    comment = commentFormat % (sys.argv[0], SVN_ID, datestamp)
    html = HTML_FORMAT % (specFile, comment, specFile, baseSpecFile, specFile, '\n'.join(plotList))
    #------------------
    # copy the SPEC data file to the WWW site, only if file has newer mtime
    wwwSpecFile = os.path.join(basedir, baseSpecFile)
    if os.path.exists(wwwSpecFile):
        wwwSpecFile_mtime = os.path.getmtime(wwwSpecFile)
	if specFile_mtime > wwwSpecFile_mtime:
	    # specFile is newer, copy to WWW site
	    shutil.copy2(specFile,wwwSpecFile)
    else:
        # copy specFile to WWW site
	shutil.copy2(specFile,wwwSpecFile)
    #------------------
    htmlFile = os.path.join(basedir, "index.html")
    f = open(htmlFile, "w")
    f.write(html)
    f.close()


if __name__ == '__main__':
    specFile = SPEC_FILE
    if len(sys.argv) > 0:
        specFile = sys.argv[1]
    plotAllSpecFileScans(specFile)
