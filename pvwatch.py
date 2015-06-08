#!/APSshare/anaconda/x86_64/bin/python

'''
watch the USAXS EPICS process variables and periodically write them to a file

Start this with the shell command::

    /APSshare/anaconda/x86_64/bin/python ./pvwatch.py >>& log.txt

'''


import datetime         # date/time stamps
import epics            # manages EPICS (PyEpics) connections for Python 2.6+
import numpy
import os.path          # testing if a file exists
import shutil           # file copies
import sys              # for flushing log output
import time             # provides sleep()
import traceback
from xml.dom import minidom
from xml.etree import ElementTree

import localConfig      # definitions for 9-ID
import scanplots
import wwwServerTransfers

try:
    # better reporting of SEGFAULT
    # http://faulthandler.readthedocs.org
    import faulthandler
    faulthandler.enable()
    print "#= %d --faulthandler" % os.getpid() + "-"*10 + " module enabled"
except ImportError, exc:
    print "#= %d --faulthandler" % os.getpid() + "-"*10 + " module not imported"


SVN_ID = "$Id$"


global GLOBAL_MONITOR_COUNTER
global pvdb         # cache of last known good values
global xref         # cross-reference between mnemonics and PV names: {mne:pvname}

GLOBAL_MONITOR_COUNTER = 0
pvdb = {}   # EPICS data will go here
xref = {}   # cross-reference id with PV
PVLIST_FILE = "pvlist.xml"
MAINLOOP_COUNTER_TRIGGER = 10000  # print a log message periodically
USAXS_DATA = None


'''value for expected EPICS PV is None'''
class NoneEpicsValue(Exception): pass

'''pv not in pvdb'''
class PvNotRegistered(Exception): pass


def logMessage(msg):
    '''write a message with a timestamp and pid to the log file'''
    scriptName = os.path.basename(sys.argv[0])
    print "[%s %d %s] %s" % (scriptName, os.getpid(), getTime(), msg)
    sys.stdout.flush()


def logException(troublemaker):
    '''write an exception report to the log file'''
    msg = "problem with %s:" % troublemaker
    for _ in msg.splitlines():
        logMessage(_)
    for _ in traceback.format_exc().splitlines():
        logMessage('\t' + _)


def getSpecFileName(pv):
    '''construct the name of the file, based on a PV'''
    dir_pv = xref['spec_dir']
    userDir = pvdb[dir_pv]['value']
    rawName = pvdb[pv]['value']
    if userDir is None:
        raise NoneEpicsValue, '"None" received for spec_dir PV: <' + str(dir_pv) + '>'
    if rawName is None:
        raise NoneEpicsValue, '"None" received for spec file PV: <' + str(pv) + '>'
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

    plotFile = localConfig.LOCAL_PLOTFILE
    plotFile = os.path.join(localConfig.LOCAL_WWW_LIVEDATA_DIR, plotFile)
    makePlot = not os.path.exists(plotFile)        # no plot yet, let's make one!
    if os.path.exists(plotFile):
        plot_mtime = os.stat(plotFile).st_mtime
        makePlot = spec_mtime > plot_mtime        #  plot only if new data

    if makePlot:
        #logMessage("updating the plots and gathering scan data for XML file")
        scanplots.main(n=localConfig.NUM_SCANS_PLOTTED, cp=True)


def writeFile(filename, contents):
    '''write contents to file'''
    f = open(filename, 'w')
    f.write(contents)
    f.close()


def xslt_transformation(xslt_file, src_xml_file, result_xml_file):
    '''transform an XML file using an XSLT'''
    # see: http://lxml.de/xpathxslt.html#xslt
    from lxml import etree as lxml_etree      # in THIS routine, use lxml's etree
    src_doc = lxml_etree.parse(src_xml_file)
    xslt_doc = lxml_etree.parse(xslt_file)
    transform = lxml_etree.XSLT(xslt_doc)
    result_doc = transform(src_doc)
    buf = lxml_etree.tostring(result_doc, pretty_print=True)
    writeFile(result_xml_file, buf)


def textArray(arr):
    '''convert an ndarray to a text array'''
    if isinstance(arr, numpy.ndarray):
        return [str(_) for _ in arr]
    return arr


def buildReport():
    '''build the report'''
    t = datetime.datetime.now()
    yyyymmdd = t.strftime("%Y-%m-%d")
    hhmmss = t.strftime("%H:%M:%S")

    root = ElementTree.Element("usaxs_pvs")
    root.set("version", "1")
    node = ElementTree.SubElement(root, "written_by")
    node.text = SVN_ID
    node = ElementTree.SubElement(root, "datetime")
    node.text = yyyymmdd + " " + hhmmss

    sorted_id_list = sorted(xref)
    fields = ("name", "id", "description", "timestamp",
              "counter", "units", "value", "raw_value", "format")

    for mne in sorted_id_list:
        pv = xref[mne]
        entry = pvdb[pv]

        node = ElementTree.SubElement(root, "pv")
        node.set("id", mne)
        node.set("name", pv)

        for item in fields:
            subnode = ElementTree.SubElement(node, item)
            subnode.text = str(entry[item])

    global USAXS_DATA
    if USAXS_DATA is not None and USAXS_DATA.get('usaxs', None) is not None:
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
            # write the scan data to the XML file
            vec = ElementTree.SubElement(scannode, "Q")
            vec.set('units', '1/A')
            vec.text = ' '.join(textArray(scan['qVec']))
            vec = ElementTree.SubElement(scannode, "R")
            vec.set('units', 'arbitrary')
            vec.text = ' '.join(textArray(scan['rVec']))
        except Exception, e:
            logMessage('caught Exception while writing USAXS scan data to XML file')
            logMessage('  file: %s' % specfile)
            logMessage(e)

    # final steps
    # ProcessingInstruction for 2nd line of XML
    # Cannot place this with ElementTree where it is needed
    # use minidom
    doc = minidom.parseString(ElementTree.tostring(root))
    # <?xml-stylesheet type="text/xsl" href="raw-table.xsl" ?>
    # insert XML Processing Instruction text after first line of XML
    pi = doc.createProcessingInstruction('xml-stylesheet',
                                     'type="text/xsl" href="raw-table.xsl"')
    root = doc.firstChild
    doc.insertBefore(pi, root)
    xmlText = doc.toxml()       # all on one line, looks bad, who cares?
    #xmlText = doc.toprettyxml(indent = "  ") # toprettyxml() adds extra unwanted whitespace
    return xmlText


def report():
    '''write the values out to files'''

    xmlText = buildReport()

    # WWW directory for livedata (absolute path)
    localDir = localConfig.LOCAL_WWW_LIVEDATA_DIR

    #--- write the XML with the raw data from EPICS
    raw_xml = localConfig.XML_REPORT_FILE
    abs_raw_xml = os.path.join(localDir, raw_xml)
    writeFile(abs_raw_xml, xmlText)
    wwwServerTransfers.scpToWebServer(abs_raw_xml, raw_xml)

    #--- xslt transforms from XML to HTML

    # make the index.html file
    index_html = localConfig.HTML_INDEX_FILE  # short name
    abs_index_html = os.path.join(localDir, index_html)  # absolute path
    xslt_transformation(localConfig.LIVEDATA_XSL_STYLESHEET, abs_raw_xml, abs_index_html)
    wwwServerTransfers.scpToWebServer(abs_index_html, index_html)  # copy to XSD

    # display the raw data (but pre-convert it in an html page)
    raw_html = localConfig.HTML_RAWREPORT_FILE
    abs_raw_html = os.path.join(localDir, raw_html)
    xslt_transformation(localConfig.RAWTABLE_XSL_STYLESHEET, abs_raw_xml, abs_raw_html)
    wwwServerTransfers.scpToWebServer(abs_raw_html, raw_html)

    # also copy the raw table XSLT
    xslFile = localConfig.RAWTABLE_XSL_STYLESHEET
    wwwServerTransfers.scpToWebServer(xslFile, xslFile)

    # make the usaxstv.html file
    usaxstv_html = localConfig.HTML_USAXSTV_FILE  # short name
    abs_usaxstv_html = os.path.join(localDir, usaxstv_html)  # absolute path
    xslt_transformation(localConfig.USAXSTV_XSL_STYLESHEET, abs_raw_xml, abs_usaxstv_html)
    wwwServerTransfers.scpToWebServer(abs_usaxstv_html, usaxstv_html)  # copy to XSD


def getTime():
    '''return a datetime value'''
    dt = datetime.datetime.now()
    return dt


def update_pvdb(pv, raw_value):
    if pv not in pvdb:
        msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
        raise PvNotRegistered, msg
    entry = pvdb[pv]
    #ch = entry['ch']
    entry['timestamp'] = getTime()
    entry['counter'] += 1
    entry['raw_value'] = raw_value
    entry['value'] = entry['format'] % raw_value


def EPICS_monitor_receiver(*args, **kws):
    '''Response to an EPICS (PyEpics) monitor on the channel'''
    global GLOBAL_MONITOR_COUNTER
    pv = kws['pvname']
    if pv not in pvdb:
        msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
        raise PvNotRegistered, msg
    update_pvdb(pv, kws['value'])   # cache the last known good value
    GLOBAL_MONITOR_COUNTER += 1


def add_pv(mne, pv, desc, fmt):
    '''Connect to another EPICS (PyEpics) process variable'''
    if pv in pvdb:
        raise Exception("%s already defined by id=%s" % (pv, pvdb[pv]['id']))
    ch = epics.PV(pv)
    #ch.connect()
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
    ch.add_callback(EPICS_monitor_receiver)  # start callbacks now
    cv = ch.get_ctrlvars()
    unit_renames = {        # handle some non SI unit names
        # old      new
        'millime': 'mm',
        'millira': 'mr',
        'degrees': 'deg',
        'Volts':   'V',
        'VDC':     'V',
        'eng':     '',
    }
    if cv is not None and 'units' in cv:
        units = cv['units']
        if units in unit_renames:
            units = unit_renames[units]
        entry['units'] = units
    update_pvdb(pv, ch.get())   # initialize the cache


def initiate_PV_connections():
    '''create connections to all defined PVs'''
    if not os.path.exists(PVLIST_FILE):
        logMessage('could not find file: ' + PVLIST_FILE)
        return
    try:
        tree = ElementTree.parse(PVLIST_FILE)
    except:
        logMessage('could not parse file: ' + PVLIST_FILE)
        return

    for key in tree.findall(".//EPICS_PV"):
        if key.get("_ignore_", "false").lower() == "false":
            mne = key.get("mne")
            pv = key.get("PV")
            desc = key.get("description")
            fmt = key.get("display_format", "%s")  # default format
            try:
                add_pv(mne, pv, desc, fmt)
            except:
                msg = "%s: problem connecting: %s" % (PVLIST_FILE, ElementTree.tostring(key))
                logException(msg)


def main_event_loop_checks(mainLoopCount, nextReport, nextLog, delta_report, delta_log):
    '''check events for the main event loop'''
    global GLOBAL_MONITOR_COUNTER
    global MAINLOOP_COUNTER_TRIGGER
    dt = getTime()
    epics.ca.poll()

    if mainLoopCount == 0:
        logMessage(" %s times through main loop" % MAINLOOP_COUNTER_TRIGGER)

    if dt >= nextReport:
        nextReport = dt + delta_report

        try: report()                                   # write contents of pvdb to a file
        except Exception: logException("report()")

        try: updateSpecMacroFile()                      # copy the spec macro file
        except Exception as exc: logException("updateSpecMacroFile()")

        try: updatePlotImage()                          # update the plot
        except Exception as exc: logException("updatePlotImage()")

    if dt >= nextLog:
        nextLog = dt + delta_log
        msg = "checkpoint, %d EPICS monitor events received" % GLOBAL_MONITOR_COUNTER
        logMessage(msg)
        GLOBAL_MONITOR_COUNTER = 0  # reset

    return nextReport, nextLog


def main():
    '''
    run the main event loop
    '''
    global GLOBAL_MONITOR_COUNTER
    test_pv = 'S:SRcurrentAI'
    epics.caget(test_pv)
    ch = epics.PV(test_pv)
    epics.ca.poll()
    connected = ch.connect(timeout=5.0)
    if not connected:
        print 'Did not connect PV:', ch, '  program has exited'
        return

    logMessage("starting pvwatch.py")
    initiate_PV_connections()

    logMessage("Connected %d EPICS PVs" % len(pvdb))

    nextReport = getTime()
    nextLog = nextReport
    delta_report = datetime.timedelta(seconds=localConfig.REPORT_INTERVAL_S)
    delta_log = datetime.timedelta(seconds=localConfig.LOG_INTERVAL_S)
    
    # !!!!!!!!!!!!!!!!!!!!!!! #
    # run the main event loop #
    # !!!!!!!!!!!!!!!!!!!!!!! #
    mainLoopCount = 0
    while True:     
        mainLoopCount = (mainLoopCount + 1) % MAINLOOP_COUNTER_TRIGGER
        nextReport, nextLog = main_event_loop_checks(mainLoopCount,
                                       nextReport, nextLog, delta_report, delta_log)
        time.sleep(localConfig.SLEEP_INTERVAL_S)

    # this exit handling will never be called
    for pv in pvdb:
        ch = pvdb[pv]['ch']
        if ch != None:
            ch.disconnect()
    print "script is done"


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
