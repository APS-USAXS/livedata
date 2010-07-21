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

import sys              # for flushing log output
import time             # provides sleep()
import datetime         # date/time stamps
import shutil           # file copies
import subprocess       # calling other software (xsltproc)
import shlex            # parsing command lines (for xsltproc)
import os.path          # testing if a file exists
import pvConnect        # manages EPICS connections
import pvlist   # the list of PVs to be watched
import prjPySpec        # read SPEC data files
import plot             # makes PNG files of recent USAXS scans


global GLOBAL_MONITOR_COUNTER
global pvdb
global xref
global EXC_FMT

   #@TODO: check for 15ID-D readiness
BASE_NFS = "/home/beams/S15USAXS/Documents/eclipse/USAXS/livedata"
GLOBAL_MONITOR_COUNTER = 0
LOG_INTERVAL_S = 60*5
NUM_SCANS_PLOTTED = 5
REPORT_FILE = "./www/report.xml"
REPORT_INTERVAL_S = 10
SLEEP_INTERVAL_S = 0.1
SVN_ID = "$Id$"
XSL_STYLESHEET = "raw-table.xsl"


pvdb = {}   # EPICS data will go here
xref = {}   # cross-reference id with PV

def logMessage(msg):
    '''write a message with a timestamp and pid to the log file'''
    print "[%d %s] %s" % (os.getpid(), getTime(), msg)
    sys.stdout.flush()


def logException(troublemaker):
    '''write an exception report to the log file'''
    msg = "problem with %s:" % troublemaker
    fmt = "\n  type=%s"
    fmt += "\n  value=%s"
    #fmt += "\n  stacktrace=%s"
    msg += fmt % sys.exc_info()[:2]
    #msg += "\n  type: %s\n  value: %s\n  traceback: %s" % sys.exc_info()
    logMessage(msg)


def monitor_receiver(epics_args, user_args):
    '''Response to an EPICS monitor on the channel, uses pvConnect module
       @param value: str(epics_args['pv_value'])'''
    global GLOBAL_MONITOR_COUNTER
    ch = user_args[0]
    pv = ch.GetPv()
    entry = pvdb[pv]
    value = ch.GetValue()
    entry['timestamp'] = getTime()
    entry['counter'] += 1
    entry['raw_value'] = value
    entry['value'] = entry['format'] % value
    GLOBAL_MONITOR_COUNTER += 1
    try:
        # update the units, if possible
        if entry['units'] != epics_args['pv_units']:
            entry['units'] = epics_args['pv_units']
    except:
        pass    # some PVs have no "units", ignore these transgressions
    #print 'monitor_receiver: ', pv, ' = ', value, epics_args


def add_pv(item):
    '''Connect to another EPICS process variable, uses pvConnect module'''
    my_id = item[0]
    pv = item[1]
    desc = item[2]
    if len(item) > 3:
        fmt = item[3]   # specified display format
    else:
        fmt = "%s"      # default display format
    if pv in pvdb:
        raise Exception("%s already defined by id=%s" % (pv, pvdb[pv]['id']))
    ch = pvConnect.EpicsPv(pv)
    ch.SetUserArgs(ch)
    ch.connectw()
    ch.SetUserCallback(monitor_receiver)
    ch.monitor()
    entry = {}
    entry['name'] = pv
    entry['id'] = my_id
    entry['description'] = desc
    entry['timestamp'] = None
    entry['counter'] = 0
    entry['units'] = ""
    entry['ch'] = ch
    entry['format'] = fmt       # format for display
    entry['value'] = None       # formatted value
    entry['raw_value'] = None   # unformatted value
    pvdb[pv] = entry
    xref[my_id] = pv            # allows this code to call by "id" (can change PV only in pvlist.xml then)


def makeSimpleTag(tag, value):
    '''create a simple XML tag/value string'''
    if len(str(value))>0:
        s = "<%s>%s</%s>" % (tag, value, tag)
    else:
        s = "<%s/>" % tag
    return s


def getSpecFileName(pv):
    '''construct the name of the file, based on a PV'''
    userDir = pvdb[xref['spec_dir']]['value']
    rawName = pvdb[pv]['value']
    specFile = userDir + "/" + rawName
    return specFile


def updateSpecMacroFile():
    '''copy the current SPEC macro file to the WWW page space'''
    specFile = getSpecFileName(xref['spec_macro_file'])
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
    '''make a new PNG file with the most recent USAXS scans'''
    specFile = getSpecFileName(xref['spec_data_file'])
    if not os.path.exists(specFile):
        return
    spec_mtime = os.stat(specFile).st_mtime
    if not os.path.exists(plot.PLOTFILE):
        # no plot yet, let's make one!
        plot.update_n_plots(specFile, NUM_SCANS_PLOTTED)
        return
    plot_mtime = os.stat(plot.PLOTFILE).st_mtime
    if spec_mtime > plot_mtime:
        #  plot only if new data
        plot.update_n_plots(specFile, NUM_SCANS_PLOTTED)


def shellCommandToFile(command, outFile):
    '''execute a shell command and write its output to a file'''
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    f = p.stdout
    p.wait()
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
    sorted_id_list = sorted(xref)
    field_list = []
    field_list.append("name")
    field_list.append("id")
    field_list.append("description")
    field_list.append("timestamp")
    field_list.append("counter")
    field_list.append("units")
    field_list.append("value")
    field_list.append("raw_value")
    field_list.append("format")
    for my_id in sorted_id_list:
        pv = xref[my_id]
        entry = pvdb[pv]
        ch = entry['ch']
        xml.append('  <pv id="%s" name="%s">' % (my_id, pv))
        for item in field_list:
            xml.append("    " + makeSimpleTag(item, entry[item]))
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
            for row in pvlist.pvconfig:
                #print "ROW: ", row
                try:
                    add_pv(row)
                except:
                    logException("pvlist.xml row: %s" % row)
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
                        report()                # write contents of pvdb to a file
                    except:
                        # report the exception
                        logException("report()")
                    try:
                        updateSpecMacroFile()   # copy the spec macro file
                    except:
                        # report the exception
                        logException("updateSpecMacroFile()")
                    try:
                        updatePlotImage()       # update the plot
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
