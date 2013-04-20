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


import datetime         # date/time stamps
import os.path          # testing if a file exists
import shlex            # parsing command lines (for xsltproc)
import shutil           # file copies
import subprocess       # calling other software (xsltproc)
import sys              # for flushing log output
import time             # provides sleep()
from xml.dom import minidom
from xml.etree import ElementTree
import pvConnect        # manages EPICS connections
import prjPySpec        # read SPEC data files
import plot             # makes PNG files of recent USAXS scans
import localConfig      # definitions for 15ID
import wwwServerTransfers

SVN_ID = "$Id$"


global GLOBAL_MONITOR_COUNTER
global pvdb
global xref

GLOBAL_MONITOR_COUNTER = 0
pvdb = {}   # EPICS data will go here
xref = {}   # cross-reference id with PV
PVLIST_FILE = "pvlist.xml"
MAINLOOP_COUNTER_TRIGGER = 10000  # print a log message periodically
USAXS_DATA = None


def logMessage(msg):
    '''write a message with a timestamp and pid to the log file'''
    try:
        scriptName
    except:
        scriptName = os.path.basename(sys.argv[0])
    print "[%s %d %s] %s" % (scriptName, os.getpid(), getTime(), msg)
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


def add_pv(mne, pv, desc, fmt):
    '''Connect to another EPICS process variable, uses pvConnect module'''
    if pv in pvdb:
        raise Exception("%s already defined by id=%s" % (pv, pvdb[pv]['id']))
    ch = pvConnect.EpicsPv(pv)
    ch.SetUserArgs(ch)
    ch.connectw()
    ch.SetUserCallback(monitor_receiver)
    ch.monitor()
    entry = {
        'name': pv,           # EPICS PV name
        'id': mne,            # symbolic name used in the python code
        'description': desc,  # text description for humans
        'timestamp': None,    # client time last monitor was received
        'counter': 0,         # number of monitor events received
        'units': "",          # engineering units
        'ch': ch,             # EPICS PV channel
        'format': fmt,        # format for display
        'value': None,        # formatted value
        'raw_value': None     # unformatted value
    }
    pvdb[pv] = entry
    xref[mne] = pv            # mne is local mnemonic, define actual PV in pvlist.xml


def getSpecFileName(pv):
    '''construct the name of the file, based on a PV'''
    userDir = pvdb[xref['spec_dir']]['value']
    rawName = pvdb[pv]['value']   #@TODO: What if rawName is an empty string?
    specFile = userDir + "/" + rawName
    return specFile


def updateSpecMacroFile():
    '''copy the current SPEC macro file to the WWW page space'''
    #@TODO: What if the specFile is actually a directory?
    if len(pvdb[xref['spec_macro_file']]['value'].strip()) == 0:
        # SPEC file name PV is empty
        return
    specFile = getSpecFileName(xref['spec_macro_file'])
    if not os.path.exists(specFile):
        # @TODO: will this write too much to the logs?
        logMessage(specFile + " does not exist")
        return
    if not os.path.isfile(specFile):
        # @TODO: will this write too much to the logs?
	# 2010-08-19,PRJ: Certainly if the rawName is empty, now trapped above
        logMessage(specFile + " is not a file")
        return
    localDir = localConfig.LOCAL_WWW_LIVEDATA_DIR
    macroFile = localConfig.SPECMACRO_TXT_FILE
    wwwFile = os.path.join(localDir, macroFile)

    updateFile = False
    if os.path.exists(wwwFile):
        spec_mtime = os.stat(specFile).st_mtime
        www_mtime = os.stat(wwwFile).st_mtime
        if spec_mtime > www_mtime:
            updateFile = True   # only if file is newer
    else:
        updateFile = True
    if updateFile:
        shutil.copy2(specFile, wwwFile)
        wwwServerTransfers.scpToWebServer(specFile, macroFile)


def updatePlotImage():
    '''make a new PNG file with the most recent USAXS scans'''
    specFile = getSpecFileName(xref['spec_data_file'])
    if not os.path.exists(specFile):
        logMessage(specFile + " does not exist")
        return
    if not os.path.isfile(specFile):
        logMessage(specFile + " is not a file")
        return
    spec_mtime = os.stat(specFile).st_mtime

    makePlot = False
    plotFile = localConfig.LOCAL_PLOTFILE
    plotFile = os.path.join(localConfig.LOCAL_WWW_LIVEDATA_DIR, plotFile)
    if not os.path.exists(plotFile):
        makePlot = True        # no plot yet, let's make one!
    else:
        plot_mtime = os.stat(plotFile).st_mtime
        if spec_mtime > plot_mtime:
            makePlot = True        #  plot only if new data
    if makePlot:
        logMessage("updating the plots and gathering scan data for XML file")
	usaxs = plot.update_n_plots(specFile, localConfig.NUM_SCANS_PLOTTED)
	global USAXS_DATA
	USAXS_DATA = {
	    'file': specFile,
	    'usaxs': usaxs,
	}


def writeFile(file, contents):
    '''write contents to file'''
    f = open(file, 'w')
    f.write(contents)
    f.close()


def shellCommandToFile(command, outFile):
    '''execute a shell command and write its output to a file'''
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    f = p.stdout
    p.wait()
    buf = f.read()
    f.close()
    writeFile(outFile, buf)


def insertPI(xmlText, piText):
    '''insert XML Processing Instruction text after first line of XML'''
    xml = xmlText.split("\n")
    xml.insert(1, piText)
    return "\n".join(xml)


def buildReport():
    '''build the report'''
    # ProcessingInstruction for 2nd line of XML
    # Cannot place this with ElementTree where it is needed
    t = datetime.datetime.now()
    yyyymmdd = t.strftime("%Y-%m-%d")
    hhmmss = t.strftime("%H:%M:%S")

    piText = u'<?xml-stylesheet type="text/xsl" href="raw-table.xsl" ?>'

    root = ElementTree.Element("usaxs_pvs")
    root.set("version", "1")
    node = ElementTree.SubElement(root, "written_by")
    node.text = SVN_ID
    node = ElementTree.SubElement(root, "datetime")
    node.text = yyyymmdd + " " + hhmmss

    sorted_id_list = sorted(xref)
    fields = ("name", "id", "description", "timestamp", "counter", "units", "value", "raw_value", "format")

    for mne in sorted_id_list:
        pv = xref[mne]
        entry = pvdb[pv]
        #ch = entry['ch']

        #xml.append('  <pv id="%s" name="%s">' % (mne, pv))
        node = ElementTree.SubElement(root, "pv")
        node.set("id", mne)
        node.set("name", pv)

        for item in fields:
            subnode = ElementTree.SubElement(node, item)
            subnode.text = str(entry[item])
    
    global USAXS_DATA
    if USAXS_DATA is not None:
	try:
            specfile = USAXS_DATA['file']
	    node = ElementTree.SubElement(root, "usaxs_scans")
	    node.set("file", specfile)
	    for scan in USAXS_DATA['usaxs']:
	        scannode = ElementTree.SubElement(node, "scan")
		for item in ('scan', 'key', 'label'):
		    scannode.set(item, str(scan[item]))
		scannode.set('specfile', specfile)
		ElementTree.SubElement(scannode, "title").text = scan['title']
		ElementTree.SubElement(scannode, "Q").text = ' '.join(scan['qVec'])
		ElementTree.SubElement(scannode, "R").text = ' '.join(scan['rVec'])
	except Exception, e:
	    logMessage('caught Exception while writing USAXS scan data to XML file')
	    logMessage('  file: %s' % specfile)
	    logMessage(e)
    	

    # final steps
    doc = minidom.parseString(ElementTree.tostring(root))
    xmlText = doc.toprettyxml(indent = "  ")
    return insertPI(xmlText, piText)


def report():
    '''write the values out to files'''
    xmlText = buildReport()

    # WWW directory for livedata (absolute path)
    localDir = localConfig.LOCAL_WWW_LIVEDATA_DIR

    #--- write the XML with the raw data from EPICS
    file__raw_xml = localConfig.XML_REPORT_FILE
    localFile = os.path.join(localDir, file__raw_xml)
    writeFile(localFile, xmlText)
    wwwServerTransfers.scpToWebServer(localFile, file__raw_xml)

    #--- xslt transforms from XML to HTML
    xsltCommandFormat = localConfig.XSLT_COMMAND + localFile  # xslt command

    # make the index.html file
    file__index_html = localConfig.HTML_INDEX_FILE  # short name
    xslFile = localConfig.LIVEDATA_XSL_STYLESHEET   # in Python code dir
    localFile = os.path.join(localDir, file__index_html)  # absolute path
    xsltCommand = xsltCommandFormat % xslFile
    shellCommandToFile(xsltCommand, localFile)    # do the XSLT transform
    wwwServerTransfers.scpToWebServer(localFile, file__index_html)  # copy to XSD

    # display the raw data (but pre-convert it in an html page)
    file__raw_html = localConfig.HTML_RAWREPORT_FILE
    xslFile = localConfig.RAWTABLE_XSL_STYLESHEET
    localFile = os.path.join(localDir, file__raw_html)
    xsltCommand = xsltCommandFormat % xslFile
    shellCommandToFile(xsltCommand, localFile)    # do the XSLT transform
    wwwServerTransfers.scpToWebServer(localFile, file__raw_html)

    localFile = os.path.join(localDir, xslFile)
    wwwServerTransfers.scpToWebServer(localFile, xslFile)

    # make the usaxstv.html file
    file__usaxstv_html = localConfig.HTML_USAXSTV_FILE  # short name
    xslFile = localConfig.USAXSTV_XSL_STYLESHEET   # in Python code dir
    localFile = os.path.join(localDir, file__usaxstv_html)  # absolute path
    xsltCommand = xsltCommandFormat % xslFile
    shellCommandToFile(xsltCommand, localFile)    # do the XSLT transform
    wwwServerTransfers.scpToWebServer(localFile, file__usaxstv_html)  # copy to XSD


def getTime():
    '''return a datetime value'''
    dt = datetime.datetime.now()
    return dt


def main():
    '''
    run the main loop
    '''
    global GLOBAL_MONITOR_COUNTER
    test_pv = 'S:SRcurrentAI'
    if pvConnect.testConnect(test_pv):
        logMessage("starting pvwatch.py")

        ch = pvConnect.EpicsPv(test_pv)
        ch.connectw()
        ch.monitor()

        if not os.path.exists(PVLIST_FILE):
            logMessage('could not find file: ' + PVLIST_FILE)
            return
        try:
            tree = ElementTree.parse(PVLIST_FILE)
        except:
            logMessage('could not parse file: ' + PVLIST_FILE)
            return

        for key in tree.findall("//EPICS_PV"):
            if key.get("_ignore_", "false").lower() == "false":
                mne = key.get("mne")
                pv = key.get("PV")
                desc = key.get("description")
                fmt = key.get("display_format", "%s")  # default format
                try:
                    add_pv(mne, pv, desc, fmt)
                except:
                    logException(
                                 "%s: problem connecting: %s" 
                                 % (PVLIST_FILE, ElementTree.tostring(key))
                                 )
        pvConnect.CaPoll()
        logMessage("Connected %d EPICS PVs" % len(pvdb))

        nextReport = getTime()
        nextLog = nextReport
        delta_report = datetime.timedelta(seconds=localConfig.REPORT_INTERVAL_S)
        delta_log = datetime.timedelta(seconds=localConfig.LOG_INTERVAL_S)
        mainLoopCount = 0
        while True:
            dt = getTime()
            ch.chan.pend_event()

            mainLoopCount = (mainLoopCount + 1) % MAINLOOP_COUNTER_TRIGGER
            if mainLoopCount % MAINLOOP_COUNTER_TRIGGER == 0:
                logMessage(" %s times through main loop" % MAINLOOP_COUNTER_TRIGGER)

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
                GLOBAL_MONITOR_COUNTER = 0  # reset
            #print dt
            time.sleep(localConfig.SLEEP_INTERVAL_S)

        # this exit handling will never be called
        for pv in pvdb:
            ch = pvdb[pv]['ch']
            if ch != None:
                pvdb[pv]['ch'].release()
        pvConnect.on_exit()
        print "script is done"


if __name__ == '__main__':
    if pvConnect.IMPORTED_CACHANNEL:
        main()
    else:
        print "CaChannel is missing, cannot run"
