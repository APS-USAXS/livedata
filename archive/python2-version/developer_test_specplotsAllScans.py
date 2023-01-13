
'''developer routine to test specplotsAllScans.py'''

import logging
import os
import recent_spec_data_files
import shutil
import specplotsAllScans
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# recents = recent_spec_data_files.list_recent_spec_data_files()
# recents = ["/share1/USAXS_data/2021-10/10_05_Gadikota/10_05_Gadikota.dat", ]
recents = ["/share1/USAXS_data/2021-12/12_10_DexHeater/12_10_DexHeater.dat", ]
scan_numbers = map(str, (5, 11, 17, 23, 29))

sys.argv += recents

specplotsAllScans.main(force_plot=True, scanlist=scan_numbers)
