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

import sys		# for flushing log output
import time		# provides sleep()
import datetime		# date/time stamps
import shutil		# file copies
import subprocess	# calling other software (xsltproc)
import shlex		# parsing command lines (for xsltproc)
import os.path		# testing if a file exists
import pvConnect	# manages EPICS connections
from pvlist import *	# the list of PVs to be watched
import prjPySpec	# read SPEC data files
import plot		# makes PNG files of recent USAXS scans


global GLOBAL_MONITOR_COUNTER
global pvdb
global EXC_FMT

BASE_NFS = "/home/joule/USAXS/www/livedata"
GLOBAL_MONITOR_COUNTER = 0
LOG_INTERVAL_S = 60*5
NUM_SCANS_PLOTTED = 5
REPORT_FILE = "./www/report.xml"
REPORT_INTERVAL_S = 10
SLEEP_INTERVAL_S = 0.1
SVN_ID = "$Id$"
XSL_STYLESHEET = "raw-table.xsl"


pvdb = {}   # EPICS data will go here


def logMessage(msg):
    '''write a message with a timestamp and pid to the log file'''
    print "[%d %s] %s" % (os.getpid(), getTime(), msg)
    sys.stdout.flush()


def logException(troublemaker):
    '''write an exception report to the log file'''
    fmt = "problem with %s:" % troublemaker
    fmt += "\n  type=%s"
    fmt += "\n  value=%s"
    #fmt += "\n  stacktrace=%s"
    logMessage(fmt % sys.exc_info()[:2])


def monitor_receiver(epics_args, user_args):
    '''Response to an EPICS monitor on the channel, uses pvConnect module
       @param value: str(epics_args['pv_value'])'''
    global GLOBAL_MONITOR_COUNTER
    ch = user_args[0]
    pv = ch.GetPv()
    value = ch.GetValue()
    pvdb[pv]['timestamp'] = getTime()
    pvdb[pv]['counter'] += 1
    GLOBAL_MONITOR_COUNTER += 1
    try:
        # update the units, if possible
	if pvdb[pv]['units'] != epics_args['pv_units']:
            pvdb[pv]['units'] = epics_args['pv_units']
    except:
        pass	# some PVs have no "units", ignore these transgressions
    #print 'monitor_receiver: ', pv, ' = ', value, epics_args


def add_pv(item):
    '''Connect to another EPICS process variable, uses pvConnect module'''
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
    entry['counter'] = 0
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
	plot.updatePlotImage(specFile, NUM_SCANS_PLOTTED)
    	return
    plot_mtime = os.stat(plot.PLOTFILE).st_mtime
    if spec_mtime > plot_mtime:
        #  plot only if new data
        plot.updatePlotImage(specFile, NUM_SCANS_PLOTTED)


def shellCommandToFile(command, outFile):
    '''execute a shell comannd and write its output to a file'''
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    f = p.stdout
    buf = f.read()
    f.close()
    f = open(outFile, 'w')
    f.write(buf)
    f.close()


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
    shellCommandToFile(
        "/usr/bin/xsltproc --novalid livedata.xsl " + REPORT_FILE, 
	"./www/index.html"
    )
    shellCommandToFile(
        "/usr/bin/xsltproc --novalid raw-table.xsl " + REPORT_FILE, 
	"./www/raw-report.html"
    )


def getTime():
    '''return a datetime value'''
    dt = datetime.datetime.now()
    return dt


if __name__ == '__main__':
    GLOBAL_MONITOR_COUNTER
    if pvConnect.IMPORTED_CACHANNEL:
        test_pv = 'S:SRcurrentAI'
        if pvConnect.testConnect(test_pv):
	    logMessage("starting pvwatch.py")

	    ch = pvConnect.EpicsPv(test_pv)
	    ch.connectw()
	    ch.monitor()
	    for row in pvconfig:
	    	#print "ROW: ", row
		try:
	    	    add_pv(row)
		except:
		    logMessage("Could not add this information: %s" % row)
	    pvConnect.CaPoll()
	    logMessage("Connected %d EPICS PVs" % len(pvdb))

	    nextReport = getTime()
	    nextLog = nextReport
	    delta_report = datetime.timedelta(seconds=REPORT_INTERVAL_S)
	    delta_log = datetime.timedelta(seconds=LOG_INTERVAL_S)
	    while True:
		dt = getTime()
		ch.chan.pend_event()
		if dt >= nextReport:
		    nextReport = dt + delta_report
		    try:
                        report()    		# write contents of pvdb to a file
		    except:
		    	# report the exception
			logException("report()")
		    try:
                        updateSpecMacroFile()	# copy the spec macro file
		    except:
		    	# report the exception
			logException("updateSpecMacroFile()")
		    try:
                        updatePlotImage()	# update the plot
		    except:
			logException("updatePlotImage()")
		if dt >= nextLog:
		    nextLog = dt + delta_log
                    logMessage(
		        "checkpoint, %d EPICS monitor events received" 
			% GLOBAL_MONITOR_COUNTER
		    )
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
