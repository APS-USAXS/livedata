#!/usr/bin/env python

'''read XML configuration files into a common data structure'''

import os.path
import re
import sys
import time
from xml.etree import ElementTree
import xml.dom.minidom

#**************************************************************************

def readPvlistXML(xmlFile):
    '''get the list of PVs to monitor from the XML file'''
    doc = openScanLogFile(xmlFile)
    xref = {}
    if doc != None:
        db = []
        for element in doc.findall('EPICS_PV'):
            arr = {}
            arr['desc'] = element.text.strip()
            for attribute in element.attrib.keys():
                arr[attribute] = element.attrib[attribute].strip()
            db.append(arr)
        xref['pvList'] = db
        xref['scanLogFile'] = doc.find('scanLog_file').text
        xref['local_www_dir'] = doc.find('local_www_dir').text
    return(xref)

#**************************************************************************

def readConfigurationXML(pvListFile):
    '''locate the PV configuration from XML into memory'''
    return readPvlistXML(pvListFile)

#**************************************************************************

def openScanLogFile(xmlFile):
    '''
    open the XML file with ElementTree
    return the doc (doc.getroot() to get the root node)
    '''
    doc = None
    try:
        doc = ElementTree.parse(xmlFile)
    except:
        pass
    return doc

#**************************************************************************

def locateScanID(doc, scanid):
    '''
    find the XML scan entry with matching id attribute
    return XML node or None if not found
    '''
    result = None
    #query = "scan/[@id='%s']" % scanid
    for node in doc.findall("scan"):
        if node.get("id") == scanid:
            result = node
            break
    return result

#**************************************************************************

def flagRunawayScansAsUnknown(doc, scanid):
    '''sometimes, a scan ends without this program finding out'''
    for node in doc.findall("scan"):            # look for any scan ...
        if node.get("state") == "scanning":     # with state="scanning" ...
            if node.get("id") != scanid:        # but not the newest node ...
                node.set("state", "unknown")    # THIS node is not scanning anymore

#**************************************************************************

def readFileAsLines(filename):
    '''
    open a file and read all of it into 
    memory as a list separated by line breaks,
    return None if error or cannot find file
    '''
    if not os.path.exists(filename):
        return None
    try:
        f = open(filename, 'r')
        buf = f.read()
        f.close()
        return buf.split("\n")
    except:
        return None

#**************************************************************************

def writeLinesInFile(filename, lines):
    '''write a list of lines to a file, ignore any errors'''
    try:
        f = open(filename, 'w')
        f.write("\n".join(lines) + "\n")
        f.close()
    except:
        pass

#**************************************************************************

def prettyXml(element):
    '''fallback support for better code'''
    return prettyXmlToString(element)


def prettyXmlToString(element):
    '''
    make nice-looking XML that is human-readable
    @see http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
    '''
    txt = ElementTree.tostring(element)
    dom = xml.dom.minidom.parseString(txt)
    ugly = dom.toprettyxml()
    #pretty = dom.toxml()
    text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
    pretty = text_re.sub('>\g<1></', ugly)
    return "\n".join(removeBlankLines(pretty.split("\n")))

#**************************************************************************

def removeBlankLines(lines):
    result = []
    for line in lines:
        if len(line.strip()) > 0:
            result.append(line)
    return result

#**************************************************************************

def writeXmlDocToFile(xmlFile, doc):
    '''write the XML doc to a file'''
    # splice in the reference to the XSLT at the top of the file (on line 2)
    xsltRef = '<?xml-stylesheet type="text/xsl" href="scanlog.xsl" ?>'
    lines = prettyXmlToString(doc.getroot()).split("\n")
    lines.insert(1, xsltRef)
    writeLinesInFile(xmlFile, lines)
    return

#**************************************************************************

def appendTextNode(doc, parent, tag, value):
    '''append a text node to the XML document'''
    elem = ElementTree.Element(tag)
    elem.text = value
    parent.append(elem)

#**************************************************************************

def appendDateTimeNode(doc, parent, tag):
    '''append a date/time node to the XML document'''
    elem = ElementTree.Element(tag)
    elem.set('date', xmlDate())
    elem.set('time', xmlTime())
    parent.append(elem)

#**************************************************************************

def xmlDate():
    '''current date, for use in XML file (ISO8601)'''
    txt = time.strftime('%Y-%m-%d')    # XML date format
    return txt

#**************************************************************************

def xmlTime():
    '''current time, for use in XML file (ISO8601)'''
    txt = time.strftime('%H:%M:%S')    # XML time format
    return txt

#**************************************************************************

def main():
    ''' test routine '''
    if (len(sys.argv) == 2):
        pwd = sys.argv[1]
    else:
        pwd = '.'
    config = readConfigurationXML(os.path.join(pwd, 'pvlist.xml'))
    if len(config) == 0:
        print "ERROR: could not read the configuration file"
        return
    doc = openScanLogFile(config['scanLogFile'])
    root = doc.getroot()
    scan = locateScanID(doc, '43:/share1/USAXS_data/2010-03/03_24_setup.dat')
    scan.set("gotcha", "True")
    print prettyXmlToString(scan)
    appendTextNode(doc, root, "modifed.by", sys.argv[0])
    appendDateTimeNode(doc, root, "timestamp")
    #print prettyXml(root)
    writeXmlDocToFile('test.xml', doc)

#**************************************************************************

if __name__ == "__main__":
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
########### SVN repository information ###################
