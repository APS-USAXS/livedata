#!/usr/bin/env python

'''
/APSshare//epd/rh5-x86/bin/python ./checkup.py pvlist.xml | more
'''

# $Id $

from xml.etree import ElementTree
import os, sys, time
import epics

XML_FILE = 'test.xml'
XML_FILE = 'pvlist_2011-09-09.xml'
XML_FILE = 'pvlist.xml'
tree = ElementTree.parse(XML_FILE)

def basePVname(pv):
    '''' return the base part of the PV name '''
    return pv.split(".")[0]

spec = "%30s   %20s   %s"
print spec % ( "EPICS PV", "pv.DESC", "pvlist.xml description" )
print spec % ( "-"*30, "-"*20, "-"*30 )
nodelist = tree.findall(".//EPICS_PV")
for key in nodelist:
    if key.get("_ignore_", "false").lower() == "false":
        pv = key.get("PV")
	base = basePVname(pv)
 	if pv == base + ".RBV":
	    rtyp = epics.caget(base + ".RTYP")
	    if rtyp == "motor":
		mne = key.get("mne")
 		desc = key.get("description")
 		#fmt = key.get("display_format", "%s")  # default format
		text = epics.caget(base + ".DESC")
		print spec % (base, text, desc)
