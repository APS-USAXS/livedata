#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   define 15ID-D USAXS constants for these Python tools
'''

import os


# general use
HOME_DIR = "/home/beams/S15USAXS"
BASE_DIR = "/data/USAXS_data/"
WWW_BASE_DIR = os.path.join(BASE_DIR, "www")

PLOT_FORMAT = "png"
PLOTICUS = os.path.join(HOME_DIR, "bin/pl")
PLOTICUS_PREFABS = os.path.join(HOME_DIR, "Documents/ploticus/pl241src/prefabs")


# dirWatch.py
SKIP_DIRS = ['.AppleFileInfo']
KEEP_EXTS = ['.dat']
TIME_WINDOWS_SECS = 60*60*24*180
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


# plotAllSpecFileScans.py
SPECPLOTS_DIR = "./www/specplots"
SPEC_FILE = os.path.join(BASE_DIR, "2010-03/03_27.dat")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
HREF_FORMAT = "<a href=\"%s\"><img src=\"%s\" width=\"%s\" "
HREF_FORMAT += " height=\"%s\" alt=\"%s\"/></a>"
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


# plot.py
A_keV = 12.3984244
FIXED_VF_GAIN = 1e5
PLOTFILE = "www/livedata.png"


# pvwatch.py
BASE_NFS = os.path.join(HOME_DIR, "Documents/eclipse/USAXS/livedata")
LOG_INTERVAL_S = 60*5
NUM_SCANS_PLOTTED = 5
REPORT_FILE = "./www/report.xml"
REPORT_INTERVAL_S = 10
SLEEP_INTERVAL_S = 0.1
XSL_STYLESHEET = "raw-table.xsl"


# specplot.py
TEST_SPEC_DATA = os.path.join(BASE_DIR, "2010-03/03_25.dat")
TEST_SPEC_SCAN_NUMBER = 1
TEST_PLOTFILE = "pete.png"
TEST_PLOTICUS_COMMAND_FILE = "pete.pl"
LINE_ONLY_THRESHOLD = 400
