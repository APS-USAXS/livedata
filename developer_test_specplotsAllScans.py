
'''developer routine to test specplotsAllScans.py'''

import logging
import os
import recent_spec_data_files
import shutil
import specplotsAllScans
import sys

logger = logging.getLogger("pydev-shell")
logger.setLevel(logging.DEBUG)

sys.argv += recent_spec_data_files.list_recent_spec_data_files()

specplotsAllScans.main()
