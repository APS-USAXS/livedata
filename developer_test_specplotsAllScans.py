
'''developer routine to test specplotsAllScans.py'''

import logging
import os
import recent_spec_data_files
import shutil
import specplotsAllScans
import sys

logger = logging.getLogger("pydev-shell")
logger.setLevel(logging.DEBUG)

# recents = recent_spec_data_files.list_recent_spec_data_files()
recents = ["/share1/USAXS_data/2021-10/10_05_Gadikota/10_05_Gadikota.dat", ]
sys.argv += recents

specplotsAllScans.main()
