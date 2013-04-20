#!/usr/bin/env python

'''
connect with and watch EPICS PVs

Usage:

    ::
    
        from pvconnect import WatchedList
        # ...
        w = WatchedList()
        w.add('iso8601', 'morel:iso8601', 'timestamp',   '%s')
        w.add('tod',     'morel:TOD',     'time of day', '%s')

        # then store the current list values in an XML document in `pv` elements
        # this is an example:
        from lxml import etree
        root = etree.Element("usaxs_pvs")
        root.set("version", "1")
        root.set("monitored_events", str(w.getTotalCallbacks()))
        w.write_xml(root, 'pv')

Resulting XML content::

    <usaxs_pvs version="1" monitored_events="22">
      <pv id="tod" name="morel:TOD">
        <name>morel:TOD</name>
        <id>morel:TOD</id>
        <description>time of day</description>
        <timestamp>2013-04-20 10:36:29.092000</timestamp>
        <counter>11</counter>
        <units></units>
        <value>04/20/2013 10:37:04</value>
        <raw_value>04/20/2013 10:37:04</raw_value>
        <format>%s</format>
      </pv>
      <pv id="iso8601" name="morel:iso8601">
        <name>morel:iso8601</name>
        <id>morel:iso8601</id>
        <description>timestamp</description>
        <timestamp>2013-04-20 10:36:29.373000</timestamp>
        <counter>11</counter>
        <units></units>
        <value>2013-04-20T10:37:05</value>
        <raw_value>2013-04-20T10:37:05</raw_value>
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
import datetime
import epics
import time


TOTAL_CALLBACKS = 0


class WatchedPV(object):
    '''connect to and watch an EPICS PV for updates'''
    
    def __init__(self, mne, name, desc, fmt='%s'):
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
        node = etree.SubElement(parent, tag)
        node.set("id", self.mne)
        node.set("name", self.name)
        
        create = etree.SubElement
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
    
    def add(self, mne, pvname, desc, fmt='%s'):
        '''
        add a PV to the watch list
        
        :param str mne: mnemonic reference (short name), **must be unique**
        :param str pvname: EPICS process variable name
        :param str desc: description, readable by humans
        :param str fmt: display format string (default ``%s``)
        '''
        self.db[mne] = WatchedPV(mne, pvname, desc, fmt)
        self.xref[pvname] = mne
    
    def getList(self, sorted=True):
        '''
        return a list of all PyEpics objects
        
        :param bool sorted: if True (default), sort by `mne`
        '''
        if sorted:
            #keys = sorted(self.db)        # TODO: Why is this failing?
            return [self.db[mne] for mne in self.db]
        else:
            return self.db.values()
    
    def get(self, mne):
        '''return the PyEpics PV obj for `mne`'''
        return self.db.get(mne, None)
    
    def getTotalCallbacks(self):
        '''return the total number of EPICS callback events received'''
        return TOTAL_CALLBACKS
    
    def write_xml(self, parent, tag = 'pv'):
        '''adds XML `tag` nodes below `parent` for each PV in the list'''
        for obj in self.getList():
            obj.write_xml(parent, tag)


if __name__ == '__main__':
    observation_time = 10
    w = WatchedList()
    w.add('iso8601', 'morel:iso8601', 'timestamp',   '%s')
    w.add('tod',     'morel:TOD',     'time of day', '%s')
    time.sleep(observation_time)
    print w.getTotalCallbacks()
    
    root = etree.Element("usaxs_pvs")
    root.set("version", "1")
    root.set("monitored_events", str(w.getTotalCallbacks()))
    w.write_xml(root, 'pv')
    print etree.tostring(root, pretty_print=True)
