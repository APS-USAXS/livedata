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
'''

import specplot
PLOT_DIR = "./www/scanplots"
HTML_FILE = PLOT_DIR + "/index.html"
SPEC_FILE = '/share1/USAXS_data/2010-03/03_27.dat'
HREF_FORMAT = "<a href=\"%s\"><img src=\"%s\" width=\"%s\" height=\"%s\" alt=\"%s\"/></a>"


def plotAllScans(specFile, plotDir="", htmlFile="index.html"):
    '''plot all the scans found'''
    sd = specplot.openSpecFile(specFile)
    html = []
    html.append('<html>')
    html.append('<head>')
    html.append("<title>SPEC scans from %s</title>" % specFile)
    html.append('</head>')
    html.append('<body>')
    html.append("<h1>SPEC scans from: %s</h1>" % specFile)
    for scan in sd.scans:
	shortName = "s%d.png" % scan.scanNum
	plotFile = "%s/%s" % (plotDir, shortName)
        print scan.scanNum, scan.scanCmd, plotFile
	altText = "#%d: %s" % (scan.scanNum, scan.scanCmd)
	#----- make the plot here
        specplot.makePloticusPlot(specFile, scan, plotFile)
	#----- and build the index.html page
	html.append(HREF_FORMAT % (shortName, shortName, "150", "75", altText))
    html.append('</body>')
    html.append('</html>')
    #------------------
    f = open(htmlFile, "w")
    f.write("\n".join(html))
    f.close()


if __name__ == '__main__':
    plotAllScans(SPEC_FILE, PLOT_DIR, HTML_FILE)
