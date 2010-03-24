#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   watch the USAXS EPICS process variables and 
   write them to a file periodically
   
   Start this with the shell command
   /APSshare/bin/python ./pvwatch.py >>& log.txt
'''

import time		# provides sleep()
import datetime		# date/time stamps
import pvConnect	# manages EPICS connections
from pvlist import *	# the list of PVs to be watched


REPORT_INTERVAL_S = 30
SLEEP_INTERVAL_S = 0.2
REPORT_FILE = "./www/report.xml"
SVN_ID = "$Id$"


pvdb = {}   # EPICS data will go here


def monitor_receiver(epics_args, user_args):
    '''Response to an EPICS monitor on the channel
       @param value: str(epics_args['pv_value'])'''
    ch = user_args[0]
    pv = ch.GetPv()
    value = ch.GetValue()
    pvdb[pv]['timestamp'] = getTime()
    try:
        # update the units, if possible
	if pvdb[pv]['units'] != epics_args['pv_units']:
            pvdb[pv]['units'] = epics_args['pv_units']
    except:
        pass
    #print 'monitor_receiver: ', pv, ' = ', value, epics_args


def add_pv(item):
    '''Connect to another EPICS process variable'''
    id = item[0]
    pv = item[1]
    desc = item[2]
    ch = pvConnect.EpicsPv(pv)
    ch.SetUserArgs(ch)
    ch.connectw()
    ch.SetUserCallback(monitor_receiver)
    ch.monitor()
    entry = {}
    entry['name'] = pv
    entry['id'] = id
    entry['description'] = desc
    entry['timestamp'] = None
    entry['units'] = ""
    entry['ch'] = ch
    pvdb[pv] = entry


def makeSimpleTag(tag, value):
    '''create a simple XML tag/value string'''
    s = "<%s>%s</%s>" % (tag, value, tag)
    return s

def report():
    '''write the values out in XML'''
    f = open(REPORT_FILE, 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<?xml-stylesheet type="text/xsl" href="raw-table.xsl" ?>\n')
    f.write('<usaxs_pvs version="1">\n')
    f.write("  " + makeSimpleTag('writer', SVN_ID) + "\n")
    f.write("  " + makeSimpleTag('datetime', getTime()) + "\n")
    sorted_pv_list = sorted(pvdb)
    for pv in sorted_pv_list:
	entry = pvdb[pv]
	ch = entry['ch']
	f.write('  <pv id="%s" name="%s">\n' % (entry['id'], pv))
	for item in ("name", "id", "description", "timestamp", "units"):
	    f.write("    " + makeSimpleTag(item, entry[item]) + "\n")
	f.write("    " + makeSimpleTag("value", ch.GetValue()) + "\n")
	f.write('  </pv>\n')
    f.write('</usaxs_pvs>\n')
    f.close()


def getTime():
    '''return a datetime value'''
    t = time.mktime(time.gmtime())
    dt = datetime.datetime.utcfromtimestamp(t)
    return dt


if __name__ == '__main__':
    if pvConnect.IMPORTED_CACHANNEL:
        test_pv = 'S:SRcurrentAI'
        if pvConnect.testConnect(test_pv):
	    print getTime(), ": starting pvwatch.py"

	    ch = pvConnect.EpicsPv(test_pv)
	    ch.connectw()
	    ch.monitor()
	    for row in pvconfig:
	    	#print "ROW: ", row
		try:
	    	    add_pv(row)
		except:
		    pass
	    pvConnect.CaPoll()

	    nextReport = getTime()
	    delta = datetime.timedelta(seconds=REPORT_INTERVAL_S)
	    while True:
		dt = getTime()
		ch.chan.pend_event()
		if dt >= nextReport:
		    nextReport = dt + delta
                    report()
		#print dt
		time.sleep(SLEEP_INTERVAL_S)

	    # this exit handling will never be called
	    for pv in pvdb:
	        ch = pvdb[pv]['ch']
		if ch != None:
		    pvdb[pv]['ch'].release()
            pvConnect.on_exit()
	    print "script is done"
    else:
        print "CaChannel is missing, cannot run"
