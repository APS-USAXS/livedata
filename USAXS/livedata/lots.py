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

HREF_FORMAT = "<a href=\"%s\"><img src=\"%s\" width=\"%s\" height=\"%s\"/></a>"

if __name__ == '__main__':
    specFile = '/share1/USAXS_data/2010-03/03_27.dat'
    sd = specplot.openSpecFile(specFile)
    print len(sd.scans)
    html = []
    html.append('<html>')
    html.append('<head>')
    html.append("<title>SPEC scans from %s</title>" % specFile)
    html.append('</head>')
    html.append('<body>')
    html.append("<h1>SPEC scans from: %s</h1>" % specFile)
    for scan in sd.scans:
	shortName = "s%d.png" % scan.scanNum
	plotFile = "%s/%s" % (PLOT_DIR, shortName)
        print scan.scanNum, scan.scanCmd, plotFile
        specplot.makePloticusPlot(specFile, scan, plotFile)
	html.append(HREF_FORMAT % (shortName, shortName, "150", "75"))
    html.append('</body>')
    html.append('</html>')
    #------------------
    f = open(HTML_FILE, "w")
    f.write("\n".join(html))
    f.close()
