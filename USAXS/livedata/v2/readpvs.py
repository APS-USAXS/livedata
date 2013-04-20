#!/usr/bin/env python

'''
read PVs from configuration (XML) file and start watching them

Usage:

    ::
    
        from readpvs import ManagePvList
        mpvl = ManagePvList('pvlist.xml')
        
        # later, report the results in an XML document
        from lxml import etree
        root = etree.Element("usaxs_pvs")
        root.set("version", "1")
        mpvl.write_xml(root, 'pv')
        print etree.tostring(root, pretty_print=True)

*pvlist.xml* content::

    <?xml version="1.0" ?>
    <pvwatch version="1.0">
      <EPICS_PV PV="morel:iso8601" description="ISO-8601-compliant timestamp"  mne="timestamp"/>
      <EPICS_PV PV="morel:TOD"     description="time of day"                   mne="datetime"/>
    </pvwatch>

Resulting XML content::

    <usaxs_pvs version="1" monitored_events="12">
      <pv id="timestamp" name="morel:iso8601">
        <name>morel:iso8601</name>
        <id>morel:iso8601</id>
        <description>ISO-8601-compliant timestamp</description>
        <timestamp>2013-04-20 10:41:39.413000</timestamp>
        <counter>6</counter>
        <units></units>
        <value>2013-04-20T10:42:15</value>
        <raw_value>2013-04-20T10:42:15</raw_value>
        <format>%s</format>
      </pv>
      <pv id="datetime" name="morel:TOD">
        <name>morel:TOD</name>
        <id>morel:TOD</id>
        <description>time of day</description>
        <timestamp>2013-04-20 10:41:39.100000</timestamp>
        <counter>6</counter>
        <units></units>
        <value>04/20/2013 10:42:14</value>
        <raw_value>04/20/2013 10:42:14</raw_value>
        <format>%s</format>
      </pv>
    </usaxs_pvs>

'''

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


from lxml import etree
from pvconnect import WatchedList
import os
import time


class ManagePvList(object):
    '''
    Read the list of PVs from the configuration file and monitor them
    
    Reads the given XML file, looks for `EPICS_PV` tags,
    parses the information, 
    and starts monitoring them for updates from EPICS.
    
    The list of PVs is stored in self.watch_list(see :class:`WatchedList`)
    '''
    
    def __init__(self, xmlFile):
        if not os.path.exists(xmlFile):
            raise ValueError, 'File not found: ' + xmlFile
        self.xmlFile = xmlFile
        self.root = self._open()
        self.watch_list = WatchedList()
        if self.isIdentified():
            self._parse_xml_document()
        else:
            self.root = None
            self.xmlFile = None
            
    
    def _open(self):
        '''open the XML document and return its root node (called internally)'''
        if self.xmlFile is None:
            return None
        doc = etree.parse(self.xmlFile)
        return doc.getroot()
    
    def isIdentified(self):
        '''is the file identified as our pvlist.xml file?'''
        if self.root is None:
            return False
        return self.root.get('version', None) in ('1.0', )
    
    def _parse_xml_document(self):
        '''parse the open XML document and add PVs to the watch list (called internally)'''
        if self.root is None:
            return
        for node in self.root.findall('EPICS_PV'):
            if node.get('_ignore_', '') not in ('true',):
                pv = node.attrib['PV']
                desc = node.attrib['description']
                mne = node.attrib['mne']
                fmt = node.get('display_format', '%s')
                print mne, fmt, pv, desc
                # TODO: Can this return before PVs connect?  Takes too long if many are not found.
                self.watch_list.add(mne, pv, desc, fmt)
    
    def write_xml(self, parent, tag = 'pv'):
        '''adds XML `tag` nodes below `parent` for each PV in the list'''
        parent.set("monitored_events", str(self.watch_list.getTotalCallbacks()))
        self.watch_list.write_xml(parent, 'pv')


if __name__ == '__main__':
    testfile = os.path.join('..', 'pvlist.xml')
    testfile = os.path.join('test_pvlist.xml')

    mpvl = ManagePvList(testfile)
    time.sleep(5)
    root = etree.Element("usaxs_pvs")
    root.set("version", "1")
    mpvl.write_xml(root, 'pv')
    print etree.tostring(root, pretty_print=True)

    # show the PV specifications by applying an XSLT transformation
    if False:
        xslt_file = 'pvlist.xsl'
        if os.path.exists(xslt_file):
            pv_root = etree.parse(testfile)
            xslt_root = etree.parse(xslt_file)
            transform = etree.XSLT(xslt_root)
            result_tree = transform(pv_root)
            f = open('pvlist.html', 'w')
            f.write(etree.tostring(result_tree, pretty_print=True))
            f.close()
