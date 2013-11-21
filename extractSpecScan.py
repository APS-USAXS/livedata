#!/usr/bin/python
"""
extractSpecScan: pull out named columns from scan(s) in a SPEC data file and save to TSV files

:SVN:  $Id$

**Usage**::

  extractSpecScan.py /tmp/CeCoIn5 5 HerixE Ana5 ICO-C

**General usage**::

  extractSpecScan.py ./path/to/specFile  scanNumbers  columnLabels

where the path to the spec data file can be relative, absolute, 
or no directory part given at all,
the scan numbers are integers, separated by spaces and the columns 
labels are character strings (not valid integers), separated by spaces.

.. note:: TSV: tab-separated values
"""

import prjPySpec
import os
import sys

#-------------------------------------------------------------------------------------------


def makeOutputFileName(specFile, scanNum):
    '''
    return an output file name based on specFile and scanNum
    
    :param str specFile: name of existing SPEC data file to be read
    :param int scanNum: number of chosen SPEC scan

    append scanNum to specFile to get output file name 
    (before file extension if present)
    
    Examples:
    
    ===========  =======   ==============
    specFile     scanNum   outFile
    ===========  =======   ==============
    CeCoIn5      scan 5    CeCoIn5_5
    CeCoIn5.dat  scan 5    CeCoIn5_5.dat
    ===========  =======   ==============
    '''
    name_parts = os.path.splitext(specFile)
    outFile = name_parts[0] + '_' + str(scanNum) + name_parts[1]
    return outFile


def do_the_work(specFile, scanList, column_labels):
    '''
    read the data file, find each scan, find the columns, save the data
    
    :param str specFile: name of existing SPEC data file to be read
    :param [int] scanList: list of chosen SPEC scan numbers
    :param [str] column_labels: list of column labels
    
    .. note:: Each column label must match *exactly* the name of a label
       in each chosen SPEC scan number or the program will stop with
       a ValueError exception.
       
       If more than one column matches, the first match will be selected.
    
    example output::

        # USAXS.m2rp    Monitor    I0
        1.9475    65024    276
        1.9725    64845    352
        1.9975    65449    478
    
    '''
    print "program: " + sys.argv[0]
    # now open the file and read it
    specData = prjPySpec.specDataFile(specFile)
    print "read: " + specFile
    
    for scanNum in scanList:
        outFile = makeOutputFileName(specFile, scanNum)
        # assume that this data file started with #S 1 (scan 1)
        # TODO: since this might not be true for some files, make more robust
        # better to implement this into prjPySpec as noted there
        scan = specData.scans[scanNum-1]
    
        # get the column numbers corresponding to the column_labels
        column_numbers = [scan.L.index(label) for label in column_labels]
        # TODO: what if label is not found?  It raises a ValueError exception, handle it
        # For now, let Python raise this all the way to the user
    
        txt = ['# ' + '\t'.join(column_labels), ]
        for data_row in scan.data_lines:
            data_row = data_row.split()
            row_data = [data_row[col] for col in column_numbers]
            txt.append( '\t'.join(row_data) )
        result = '\n'.join(txt)
        
        fp = open(outFile, 'w')
        fp.write(result)
        fp.close()
        print "wrote: " + outFile


def parseCmdLine(cmdArgs):
    '''interpret the command-line arguments (avoid getopts, optparse, and argparse)'''

    if len(cmdArgs) < 4:
        print "usage: extractSpecScan.py specFile scanNum [scanNum [...]] col1 [col2 [col3 [...]]]"
        exit(1)

    # positional argument
    specFile = cmdArgs[1]
    if not os.path.exists(specFile):
        raise RuntimeError, "file not found: " + specFile

    # variable length argument (optparse cannot handle, argparse requires python 2.7+)
    # read the list of scan numbers as integers
    # list ends when we get to a column label
    # column labels are not integers
    pos = 2
    scanList = []
    while True:
        try:
            scanList.append( int(cmdArgs[pos]) )
            pos += 1
        except ValueError:
            break

    # variable length argument
    # all that is left on the line are column labels
    column_labels = cmdArgs[pos:]
    return specFile, scanList, column_labels


def main():
    specFile, scanList, column_labels = parseCmdLine(sys.argv)
    do_the_work(specFile, scanList, column_labels)


def test():
    # test file for sector 30 is here:
    #  /home/beams/IXS/Data/HERIX/SPEC/2013-1/Weber/CeCoIn5
    # copy it and use the scratch copy (to be safe)
    # cp /home/beams/IXS/Data/HERIX/SPEC/2013-1/Weber/CeCoIn5 /tmp
    cmdLine = sys.argv[0] + r' /tmp/CeCoIn5   5   HerixE Ana5 ICO-C'

    # alternate test data from USAXS archive
    cmdLine = sys.argv[0] + r' ./testdata/11_03_Vinod.dat   2 12   USAXS.m2rp Monitor  I0'
    
    specFile, scanList, column_labels = parseCmdLine(cmdLine.split())
    do_the_work(specFile, scanList, column_labels)


if __name__ == "__main__":
    #main()
    test()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
########### SVN repository information ###################
