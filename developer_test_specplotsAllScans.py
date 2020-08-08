
'''developer routine to test specplotsAllScans.py'''

import logging
import os
import recent_spec_data_files
import shutil
import specplotsAllScans
import sys

logger = logging.getLogger("pydev-shell")
logger.setLevel(logging.DEBUG)

# # note: made soft link to simulate this path
# # mkdir -p /home/mintadmin/Documents/usaxs_sim/USAXS_data
# # cd /
# # ln -s /home/mintadmin/Documents/usaxs_sim ./share1
# path = "/share1/USAXS_data/2019-06"

# sys.argv.append(os.path.join(path, "06_26_NXSchool0626.dat"))
# sys.argv.append(os.path.join(path, "06_27_NX2.dat"))

# f = "/share1/local_livedata/specplots/mtime_cache.txt"
# if os.path.exists(f):
#     os.remove(f)
# f = "/share1/local_livedata/specplots/2019/"
# if os.path.exists(f):
#     shutil.rmtree(f, ignore_errors=True)

filelist = recent_spec_data_files.list_recent_spec_data_files()
sys.argv += filelist

specplotsAllScans.main()
