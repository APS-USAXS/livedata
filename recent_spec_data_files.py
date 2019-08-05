#!/APSshare/anaconda/x86_64/bin/python

'''
print list of the recent SPEC data files (as noted in the scan logs)
'''


import datetime         # date/time stamps
from lxml import etree as lxml_etree
import os
import time

SCANLOG_XML_FILE = "/share1/local_livedata/scanlog.xml"
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
RECENT = 1.5 * WEEK   # 1-1/2 weeks back, in seconds
TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
RETRY_MAX = 5
RETRY_DELAY_S = 5


def list_recent_spec_data_files(since = None):
    """
    return a list of the recent SPEC data files (as noted in the scan logs)
    
    PARAMETERS
    
    since : datetime object or `None`
        earliest acceptable start time for SPEC scan
        defaults to `RECENT` (as defined above)
    
    RETURNS : [str]
        list containing absolute path name(s) of recent SPEC data file(s)
    """
    since = since or datetime.datetime.fromtimestamp(time.time() - RECENT)
    
    collection = []
    retry = RETRY_MAX
    errors = []
    while retry > 0:
        try:
            xml_doc = lxml_etree.parse(SCANLOG_XML_FILE)
            retry = 0   # success!  end the while() loop
            success = True
        except lxml_etree.XMLSyntaxError as exc:
            retry -= 1  # try again
            errors.append("#%d %.3f: %s" % (retry, time.time(), str(exc)))
            if retry > 0:
                time.sleep(RETRY_DELAY_S)
    if not success and len(errors) > 0:
        emsg = "Could not read scan log XML file in %d tries:\n" % RETRY_MAX
        emsg += "\n".join(errors)
        raise RuntimeError(emsg)
    for element in xml_doc.findall('scan'):
        """
        <scan id="4579:/share1/USAXS_data/2019-04/04_19_Gadikota.dat" number="4579" state="complete" type="FlyScan">
            <title>MgO12</title>
            <file>/share1/USAXS_data/2019-04/04_19_Gadikota.dat</file>
            <started date="2019-04-22" full="2019-04-22 22:40:17.671943" time="22:40:17"/>
            <ended date="2019-04-22" full="2019-04-22 22:41:58.581188" time="22:41:58"/>
        </scan>
        """
        timestamp = element.find('started').attrib["full"]
        scan_time = datetime.datetime.strptime(timestamp, TIME_FORMAT)
        if scan_time >= since:
            filename = element.find('file').text
            if filename not in collection and os.path.exists(filename):
                collection.append(filename)

    return collection


def main():
    print("\n".join(list_recent_spec_data_files()))


if __name__ == "__main__":
    main()
