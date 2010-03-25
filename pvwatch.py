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
import shutil		# file copies
import subprocess
import shlex
import os.path
import pvConnect	# manages EPICS connections
from pvlist import *	# the list of PVs to be watched
import prjPySpec	# read SPEC data files
import plot


REPORT_INTERVAL_S = 10
SLEEP_INTERVAL_S = 0.2
REPORT_FILE = "./www/report.xml"
SVN_ID = "$Id$"
XSL_STYLESHEET = "livedata.xsl"
NUM_SCANS_PLOTTED = 5
BASE_NFS = "/home/joule/USAXS/www/livedata"

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


def updateSpecMacroFile():
    userDir = pvdb['32idbLAX:USAXS:userDir']['ch'].GetValue()
    macro = pvdb['32idbLAX:string19']['ch'].GetValue()
    specFile = userDir + "/" + macro
    if not os.path.exists(specFile):
    	return
    wwwFile = BASE_NFS + "/" + "specmacro.txt"
    if not os.path.exists(wwwFile):
    	return
    spec_mtime = os.stat(specFile).st_mtime
    www_mtime = os.stat(wwwFile).st_mtime
    if spec_mtime > www_mtime:
        #  copy only if it is newer
	shutil.copy2(specFile, wwwFile)


def updatePlotImage():
    userDir = pvdb['32idbLAX:USAXS:userDir']['ch'].GetValue()
    userFile = pvdb['32idbLAX:USAXS:specFile']['ch'].GetValue()
    specFile = userDir + "/" + userFile
    if not os.path.exists(specFile):
    	return
    spec_mtime = os.stat(specFile).st_mtime
    if not os.path.exists(plot.PLOTFILE):
        # no plot yet, let's make one!
	plot.updatePlotImage(specFile, numScans)
    	return
    plot_mtime = os.stat(plot.PLOTFILE).st_mtime
    numScans = NUM_SCANS_PLOTTED
    if spec_mtime > plot_mtime:
        #  plot only if new data
        plot.updatePlotImage(specFile, numScans)


def report():
    '''write the values out in XML'''
    #---
    # the detector currents are calculated not read 
    # directly from EPICS but rather calculated from 
    # the voltage and gain
    #---
    xml = []
    xml.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml.append('<?xml-stylesheet type="text/xsl" href="%s" ?>' % XSL_STYLESHEET)
    xml.append('<usaxs_pvs version="1">')
    xml.append("  " + makeSimpleTag('writer', SVN_ID))
    xml.append("  " + makeSimpleTag('datetime', getTime()))
    sorted_pv_list = sorted(pvdb)
    for pv in sorted_pv_list:
	entry = pvdb[pv]
	ch = entry['ch']
	xml.append('  <pv id="%s" name="%s">' % (entry['id'], pv))
	for item in ("name", "id", "description", "timestamp", "units"):
	    xml.append("    " + makeSimpleTag(item, entry[item]))
	xml.append("    " + makeSimpleTag("value", ch.GetValue()))
	xml.append('  </pv>')
    xml.append('</usaxs_pvs>')
    #---
    f = open(REPORT_FILE, 'w')
    f.write("\n".join(xml))
    f.close()
    #--- xslt transforms
    p = subprocess.Popen(shlex.split("/usr/bin/xsltproc --novalid livedata.xsl " + REPORT_FILE ), stdout=subprocess.PIPE)
    f = p.stdout
    buf = f.read()
    f.close()
    f = open("./www/index.html", 'w')
    f.write(buf)
    f.close()
    p = subprocess.Popen(shlex.split("/usr/bin/xsltproc --novalid raw-table.xsl " + REPORT_FILE), stdout=subprocess.PIPE)
    f = p.stdout
    buf = f.read()
    f.close()
    f = open("./www/raw-report.html", 'w')
    f.write(buf)
    f.close()
    #---
    #
    # copy the spec macro file
    updateSpecMacroFile()
    # update the plot 
    updatePlotImage()


def getTime():
    '''return a datetime value'''
    #t = time.mktime(time.gmtime())
    #dt = datetime.datetime.utcfromtimestamp(t)
    dt = datetime.datetime.now()
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
