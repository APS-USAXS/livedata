#!/usr/bin/env python

'''
define 9-ID-C USAXS constants for these Python tools
'''

import os


# general use
HOME_DIR = os.environ.get('HOME', '')
BASE_DIR = "/share1/USAXS_data/"
LOCAL_DATA_DIR = "/share1"
LOCAL_USAXS_DATA_DIR = os.path.join(LOCAL_DATA_DIR, "/USAXS_data")
LOCAL_WWW_LIVEDATA_DIR = os.path.join(LOCAL_DATA_DIR, "local_livedata")

PLOT_FORMAT = "png"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


# dirWatch.py
SKIP_DIRS = ['.AppleFileInfo']
KEEP_EXTS = ['.dat']
TIME_WINDOWS_SECS = 60*60*24*180


# plotAllSpecFileScans.py
LOCAL_SPECPLOTS_DIR = os.path.join(LOCAL_WWW_LIVEDATA_DIR, "specplots")
WWW_SPECPLOTS_DIR = "specplots"
SPEC_FILE = os.path.join(LOCAL_USAXS_DATA_DIR, "2010-03/03_27.dat")
MTIME_CACHE_FILE = os.path.join(LOCAL_SPECPLOTS_DIR, 'mtime_cache.txt')

# plot.py
A_keV = 12.3984244
FIXED_VF_GAIN = 1e5
#LOCAL_PLOTFILE = "livedata" + os.extsep + PLOT_FORMAT
LOCAL_USAXSPLOTFILE = 'usaxs' + os.extsep + 'jpg'
LOCAL_SAXSPLOTFILE = 'saxs' + os.extsep + 'jpg'
LOCAL_WAXSPLOTFILE = 'waxs' + os.extsep + 'jpg'
LOCAL_USAXSSTEPPLOTFILE = 'stepusaxs' + os.extsep + 'jpg'


# pvwatch.py
SOURCECODE_BASE = os.path.join(HOME_DIR, "Documents/eclipse/USAXS/livedata")
LOG_INTERVAL_S = 60*5
NUM_SCANS_PLOTTED = 9
REPORT_INTERVAL_S = 10
SLEEP_INTERVAL_S = 0.1
XML_REPORT_FILE = "report.xml"
HTML_INDEX_FILE = "index.html"
HTML_RAWREPORT_FILE = "raw-report.html"
HTML_USAXSTV_FILE = "usaxstv.html"
LIVEDATA_PHP_PAGER = "scanpager.php"
LIVEDATA_XSL_STYLESHEET = "livedata.xsl"
RAWTABLE_XSL_STYLESHEET = "raw-table.xsl"
USAXSTV_XSL_STYLESHEET = "usaxstv.xsl"
#XSLT_COMMAND = "/usr/bin/xsltproc --novalid %s "
SPECMACRO_TXT_FILE = "specmacro.txt"



# specplot.py
# TEST_SPEC_DATA = os.path.join(LOCAL_USAXS_DATA_DIR, "2011-06/06_22_setup2.dat")
# TEST_SPEC_DATA = os.path.join("testdata", "03_19_LLNL.dat")
# TEST_SPEC_DATA = os.path.join("testdata", "03_19_LLNL-problem.dat")
# TEST_SPEC_DATA = os.path.join("testdata", "11_03_Vinod.dat")
# TEST_SPEC_DATA = '/share1/USAXS_data/2013-10/10_26_Course.dat'
# TEST_SPEC_DATA = '/share1/USAXS_data/2014-02/02_18_artune.dat'
# TEST_SPEC_DATA = '/share1/USAXS_data/2014-04/04_09_Prakash_A5.dat'
# TEST_SPEC_DATA = '/share1/USAXS_data/2014-06/06_19_Tony.dat'
# TEST_SPEC_DATA = '/share1/USAXS_data/2014-08/08_13_setup.dat'
# TEST_SPEC_DATA = '/share1/USAXS_data/2015-01/02_08_Samples.dat'
# TEST_SPEC_DATA = '/share1/USAXS_data/2016-06/06_08_DoyoonKim.dat'
TEST_SPEC_DATA = '/share1/USAXS_data/2018-01/01_22_TestHDF5.dat'

TEST_SPEC_SCAN_NUMBER = 15
TEST_PLOTFILE = "pete.png"
LINE_ONLY_THRESHOLD = 400


# FlyScan
REDUCED_FLY_SCAN_BINS   = 250       # sufficient to make a good plot
MCA_CLOCK_FREQUENCY     = 50e6      # 50 MHz clock (not stored in older FlyScan files)
FLY_SCAN_Q_MIN          = 1.01e-6   # absolute minimum Q for rebinning
FLY_SCAN_UATERM         = 1.2       # for defining Q bins


# Area Detector images
REDUCED_AD_IMAGE_BINS   = 250       # sufficient to make a good plot


HDF5_PATH_TO_IMAGE_DATA = '/entry/data/data'
