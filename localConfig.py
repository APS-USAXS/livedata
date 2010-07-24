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
LOCAL_DATA_DIR = "/data"
LOCAL_USAXS_DATA_DIR = LOCAL_DATA_DIR + "/USAXS_data"
LOCAL_WWW_LIVEDATA_DIR = LOCAL_DATA_DIR + "/www/livedata"

PLOT_FORMAT = "png"
PLOTICUS = os.path.join(HOME_DIR, "bin/pl")
PLOTICUS_PREFABS = os.path.join(HOME_DIR, "Documents/ploticus/pl241src/prefabs")


# dirWatch.py
SKIP_DIRS = ['.AppleFileInfo']
KEEP_EXTS = ['.dat']
TIME_WINDOWS_SECS = 60*60*24*180
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


# plotAllSpecFileScans.py
LOCAL_SPECPLOTS_DIR = os.path.join(LOCAL_WWW_LIVEDATA_DIR, "specplots")
WWW_SPECPLOTS_DIR = "specplots"
SPEC_FILE = os.path.join(LOCAL_USAXS_DATA_DIR, "2010-03/03_27.dat")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


# plot.py
A_keV = 12.3984244
FIXED_VF_GAIN = 1e5
LOCAL_PLOTFILE = "livedata" + os.extsep + PLOT_FORMAT


# pvwatch.py
SOURCECODE_BASE = os.path.join(HOME_DIR, "Documents/eclipse/USAXS/livedata")
LOG_INTERVAL_S = 60*5
NUM_SCANS_PLOTTED = 5
REPORT_INTERVAL_S = 10
SLEEP_INTERVAL_S = 0.1
XML_REPORT_FILE = "report.xml"
HTML_INDEX_FILE = "index.html"
HTML_RAWREPORT_FILE = "raw-report.html"
LIVEDATA_XSL_STYLESHEET = "livedata.xsl"
RAWTABLE_XSL_STYLESHEET = "raw-table.xsl"
XSLT_COMMAND = "/usr/bin/xsltproc --novalid %s "



# specplot.py
TEST_SPEC_DATA = os.path.join(LOCAL_USAXS_DATA_DIR, "2010-03/03_25.dat")
TEST_SPEC_SCAN_NUMBER = 1
TEST_PLOTFILE = "pete.png"
TEST_PLOTICUS_COMMAND_FILE = "pete.pl"
LINE_ONLY_THRESHOLD = 400
