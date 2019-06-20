
"""
test scanplots.py code

supporting issue https://github.com/APS-USAXS/livedata/issues/14
and PR https://github.com/APS-USAXS/livedata/pull/20

make SAXS & WAXS data from BS show on livedata page
"""

import logging
import scanplots

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

scanplots.pr20(100)
