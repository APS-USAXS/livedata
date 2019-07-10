
'''developer routine to test specplotsAllScans.py'''

import os
import specplotsAllScans
import sys
import logging

logger = logging.getLogger("pydev-shell")
logger.setLevel(logging.DEBUG)

# note: made soft link to simulate this path
# mkdir -p /home/mintadmin/Documents/usaxs_sim/USAXS_data
# cd /
# ln -s /home/mintadmin/Documents/usaxs_sim ./share1
path = "/share1/USAXS_data"

sys.argv.append(os.path.join(path, "06_26_NXSchool0626.dat"))

specplotsAllScans.main()
