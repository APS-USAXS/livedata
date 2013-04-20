#!/usr/bin/env python

'''
connect with and watch EPICS PVs
'''

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################


from xml.dom import minidom
from xml.etree import ElementTree
import datetime
import epics
import time


TOTAL_CALLBACKS = 0


class WatchedPV(object):
    '''connect to and watch an EPICS PV for updates'''
    
    def __init__(self, mne, name, desc, fmt):
        self.name = name            # EPICS PV name
        self.mne =  mne             # symbolic name used in the python code
        self.description = desc     # text description for humans
        self.timestamp = None       # client time last monitor was received
        self.counter = 0            # number of monitor events received
        self.units = ""             # engineering units
        self.format = fmt           # format for display
        self.value = None           # formatted value
        self.raw_value = None       # unformatted value
        self.pv = epics.PV(name, callback=self.callback)
        self.pv.connect()
    
    def callback(self, **kw):
        '''called when the PV updates'''
        global TOTAL_CALLBACKS
        TOTAL_CALLBACKS += 1
        self.counter += 1
        self.timestamp = datetime.datetime.now()
        if self.units is None:
            self.units = kw.get('units', self.units)
        self.raw_value = kw.get('value', self.raw_value)
        try:
            self.value = self.fmt % self.raw_value
        except:
            self.value = kw.get('char_value', self.value)
        print self.show()
    
    def show(self):
        '''simple report'''
        return '%s (%s) = %s' % (self.mne, self.name, str(self.value))
    
    def write_xml(self, parent, tag = 'pv'):
        '''creates, fills, and returns an XML node named `tag` below `parent`'''
        node = ElementTree.SubElement(parent, tag)
        node.set("id", self.mne)
        node.set("name", self.name)
        
        create = ElementTree.SubElement
        create(node, 'name').text        = str(self.name)
        create(node, 'id').text          = str(self.name)
        create(node, 'description').text = str(self.description)
        create(node, 'timestamp').text   = str(self.timestamp)
        create(node, 'counter').text     = str(self.counter)
        create(node, 'units').text       = str(self.units)
        create(node, 'value').text       = str(self.value)
        create(node, 'raw_value').text   = str(self.raw_value)
        create(node, 'format').text      = str(self.format)
        
        return node


class WatchedList(object):
    '''maintain a list of the PVs being watched'''
    
    def __init__(self):
        self.db = {}
        self.xref = {}
    
    def add(self, mne, name, desc, fmt):
        self.db[mne] = WatchedPV(mne, name, desc, fmt)
        self.xref[name] = mne
    
    def getList(self):
        return [self.db[mne] for mne in sorted(self.db.keys())]
    
    def get(self, mne):
        return self.db.get(mne, None)
    
    def write_xml(self, parent, tag = 'pv'):
        '''adds XML `tag` nodes below `parent` for each PV in the list'''
        for obj in self.getList():
            obj.write_xml(parent, tag)


if __name__ == '__main__':
    w = WatchedList()
    w.add('iso8601', 'morel:iso8601', 'timestamp',   '%s')
    w.add('tod',     'morel:TOD',     'time of day', '%s')
    for _ in range(10):
        time.sleep(1)
    print TOTAL_CALLBACKS
    
    root = ElementTree.Element("usaxs_pvs")
    root.set("version", "1")
    root.set("monitored_events", str(TOTAL_CALLBACKS))
    w.write_xml(root, 'pv')
    print minidom.parseString(ElementTree.tostring(root)).toprettyxml(indent = "  ")
