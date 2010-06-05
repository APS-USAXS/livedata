#!/usr/bin/python
"""

  Purpose:
  Provides a set of classes to read the contents of a spec data file.

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
########### SVN repository information ###################

  author: Pete Jemian, jemian@anl.gov
  Further comments:
  Includes the UNICAT extensions which write additional floating point
  information in the scan headers using #H/#V pairs of labels/values.
  The user should create a class instance for each spec data file,
  specifying the file reference (by path reference as needed)
  and the internal routines will take care of all that is necessary
  to read and interpret the information.
  Dependencies:
    os: operating system module
    re: regular expression module

"""

import re
import os
import sys
# from sys import *

def specScanLine_stripKey(line):
    """return everything after the first space on the line from the spec data file"""
    pos = line.find(" ")
    val = line[pos:]
    return val.strip()

#-------------------------------------------------------------------------------------------

class specDataFile:
    """contents of a spec data file"""

    fileName = ''
    parts = ''
    errMsg = ''
    headers = []
    scans = []
    readOK = -1
    def __init__(self, file):
        self.fileName = file
        self.errMsg = ''
        self.headers = []
        self.scans = []
        self.readOK = -1
        self.read()

    def read(self):
        """Reads a spec data file"""
        try:
            fp = open(self.fileName, 'r')
            buf = fp.read()
            fp.close()
        except:
            self.errMsg = "\n Could not open spec file: " + self.fileName +"\n"
            self.readOK = 1
            return
        if (buf.count('#F ') <= 0):
            self.errMsg = '\n' + self.fileName + ' is not a spec data file.\n'
            self.readOK = 2
            return
        #------------------------------------------------------
        self.parts = buf.split('\n\n#')     # Break the spec file into component scans
        del buf                             # Dispose of the input buffer memory (necessary?)
        for index, substr in enumerate(self.parts):
            if (substr[0] != '#'):          # Was "#" stripped by the buf.split() above?
                self.parts[index]= '#' + substr  # Reinstall the "#" character on each part
        #------------------------------------------------------
        # pull the information from each scan head
        for part in self.parts:
            key = part[0:2]
            if (key == "#F"):
                self.headers.append(specDataFileHeader(part))
                self.specFile = self.headers[-1].file
            elif (key == "#S"):
                self.scans.append(specDataFileScan(self.headers[-1], part))
            else:
                self.errMsg = "unknown key: %s" % key
        self.readOK = 0
        return

#-------------------------------------------------------------------------------------------

class specDataFileHeader:
    """contents of a spec data file header (#F) section"""

    def __init__(self, buf):
        #----------- initialize the instance variables
        self.comments = []
        self.date = ''
        self.epoch = 0
        self.errMsg = ''
        self.file = ''
        self.H = []
        self.O = []
        self.raw = buf
        self.interpret()
        return

    def interpret(self):
        """ interpret the supplied buffer with the spec data file header"""
        lines = self.raw.splitlines()
        i = 0
        for line in lines:
            i += 1
            key = line[0:2]
            if (key == "#C"):
                self.comments.append(specScanLine_stripKey(line))
            elif (key == "#D"):
                self.date = specScanLine_stripKey(line)
            elif (key == "#E"):
                self.epoch = int(specScanLine_stripKey(line))
            elif (key == "#F"):
                self.file = specScanLine_stripKey(line)
            elif (key == "#H"):
                self.H.append(specScanLine_stripKey(line).split())
            elif (key == "#O"):
                self.O.append(specScanLine_stripKey(line).split())
            else:
                self.errMsg = "line %d: unknown key (%s) detected" % (i, key)
        return

#-------------------------------------------------------------------------------------------

class specDataFileScan:
    """contents of a spec data file scan (#S) section"""
    
    def __init__(self, header, buf):
        self.comments = []
        self.data = {}
        self.data_lines = []
        self.date = ''
        self.errMsg = ''
        self.float = {}
        self.G = []
        self.header = header        # index number of relevant #F section previously interpreted
        self.L = []
        self.M = ''
        self.positioner = {}
        self.float = {}             # UNICAT-style floating values in the header (non-positioners)
        self.N = -1
        self.P = []
        self.Q = ''
        self.raw = buf
        self.S = ''
        self.scanNum = -1
        self.scanCmd = ''
        self.specFile = ''
        self.T = ''
        self.V = []
        self.column_first = ''
        self.column_last = ''
        self.interpret()
        return

    def interpret(self):
        """interpret the supplied buffer with the spec scan data"""
        lines = self.raw.splitlines()
        i = 0
        self.specFile = self.header.file    # this is the short name, does not have the file system path
        for line in lines:
            i += 1
	    #print "[%s] %s" % (i, line)
            key = line[0:2]
	    #print i, key
            if (key[0] == "#"):
                if (key == "#C"):
                    self.comments.append(specScanLine_stripKey(line))
                elif (key == "#D"):
                    self.date = specScanLine_stripKey(line)
                elif (key == "#G"):
                    self.G.append(specScanLine_stripKey(line))
                elif (key == "#L"):
                    # Some folks use more than two spaces!  Use regular expression(re) module
                    self.L = re.split("  +", specScanLine_stripKey(line))
                    self.column_first = self.L[0]
                    self.column_last = self.L[-1]
                elif (key == "#M"):
                    self.M = specScanLine_stripKey(line)
                elif (key == "#N"):
                    self.N = int(specScanLine_stripKey(line))
                elif (key == "#P"):
                    self.P.append(specScanLine_stripKey(line))
                elif (key == "#Q"):
                    self.Q = specScanLine_stripKey(line)
                elif (key == "#S"):
                    self.S = specScanLine_stripKey(line)
                    pos = self.S.find(" ")
                    self.scanNum = int(self.S[0:pos])
                    self.scanCmd = self.S[pos+1:]
                elif (key == "#T"):
                    self.T = specScanLine_stripKey(line)
                elif (key == "#V"):
                    self.V.append(specScanLine_stripKey(line))
                else:
                    self.errMsg = "line %d: unknown key (%s) detected" % (i, key)
            elif len(line) < 2:
                self.errMsg = "problem with  key " + key + " at scan header line " + str(i)
            elif key[1] == "@":
                self.errMsg = "cannot handle @ data yet."
            else:
                self.data_lines.append(line)
        # interpret the motor positions from the scan header
        self.positioner = {}
        for row, values in enumerate(self.P):
            for col, val in enumerate(values.split()):
                mne = self.header.O[row][col]
                self.positioner[mne] = float(val)
        # interpret the UNICAT floating point data from the scan header
        self.float = {}
        for row, values in enumerate(self.V):
            for col, val in enumerate(values.split()):
                label = self.header.H[row][col]
                self.float[label] = float(val)
        # interpret the data lines from the body of the scan
        self.data = {}
	for col in range(len(self.L)):
	    label = self.L[col]
	    # need to guard when same column label is used more than once
	    if label in self.data.keys():
	        label += "(duplicate)"
		self.L[col] = label    # rename this column's label
            self.data[label] = []
        for row, values in enumerate(self.data_lines):
            for col, val in enumerate(values.split()):
                label = self.L[col]
                self.data[label].append(float(val))
        return

#-------------------------------------------------------------------------------------------

def _test(mode):
    """test the routines that read from the spec data file
    @param mode: boolean, TRUE means spec file name is given on command line"""
    if (mode):
        # ActiveState Python returns the full path script name as argv
        # replaced previous test of
        #       len(argv)
        # with a mode selector but this will break testing on any other platform.
        # NEED TO FIX THIS
        TEST_FILE = sys.argv[-1]
    else:
        print sys.argv
        TEST_DIR = '/share1/USAXS_data/2010-03'
        TEST_FILE = '03_25.dat'
        # SPEC_FILE = '/share1/USAXS_data/2010-03/03_25.dat'
        # SPEC_FILE = '/share1/USAXS_data/2010-03/03_27.dat'
        os.chdir(TEST_DIR)
    print '-------------------------------------------------------------------'
    # now open the file and read it
    test = specDataFile(TEST_FILE)
    # tell us about the test file
    print 'file', test.fileName
    print 'OK?', test.readOK
    print 'headers', len(test.headers)
    print 'scans', len(test.scans)
    #print 'positioners in first scan:'; print test.scans[0].positioner
    for stuff in test.scans:
        print stuff.scanNum, stuff.date, 'AR', stuff.positioner['ar'], 'eV', 1e3*stuff.float['DCM_energy']
    print 'positioners in last scan:'
    print test.scans[0].positioner
    pLabel = test.scans[-1].column_first
    dLabel = test.scans[-1].column_last
    print test.scans[-1].data[pLabel]
    print len(test.scans[-1].data[pLabel])
    print pLabel, dLabel
    for i in range(len(test.scans[-1].data[pLabel])):
        print test.scans[-1].data[pLabel][i], test.scans[-1].data[dLabel][i]
    # test = specDataFile('07_02_sn281_8950.dat')
    print test.scans[0].L

if __name__ == "__main__":
    _test(0)
