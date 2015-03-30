#!/usr/bin/env python

'''
print descriptions for all motors defined in pvlist.xml

Uses PyEpics

usage::

  /APSshare//epd/rh5-x86/bin/python ./checkup.py pvlist.xml | more

'''

# $Id$

from xml.etree import ElementTree
import epics
import pyRestTable

XML_FILE = 'test.xml'
XML_FILE = 'pvlist_2011-09-09.xml'
XML_FILE = 'pvlist.xml'
tree = ElementTree.parse(XML_FILE)

def basePVname(pv):
    '''' return the base part of the PV name '''
    return pv.split(".")[0]

d = {}
for key in tree.findall(".//EPICS_PV"):
    if key.get("_ignore_", "false").lower() == "true":
        continue
    pv = key.get("PV")
    base = basePVname(pv)
    if pv == base + ".RBV":
        rtyp = epics.caget(base + ".RTYP")
        if rtyp not in ("motor", ):
	    continue
        mne = key.get("mne")
        desc = key.get("description")
        #fmt = key.get("display_format", "%s")  # default format
        text = epics.caget(base + ".DESC")
	d[mne.lower()] = (rtyp, base, mne, text, desc)

t = pyRestTable.Table()
t.labels = ( "RTYP", "EPICS PV", "mnemonic", "pv.DESC", "pvlist.xml description" )
for mne in sorted(d.keys()):
    t.rows.append( d[mne] )
print t.reST()
