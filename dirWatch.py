#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   watch a directory (and all directories beneath) for new versions of SPEC data files
'''

import os
import string
#import sys
import time


BASE_DIR = "/share1/USAXS_data/"
SKIP_DIRS = ['.AppleFileInfo']
KEEP_EXTS = ['.dat']
TIME_WINDOWS_SECS = 60*60*24*180
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


class dirWatch:
    '''get the mtime from SPEC data files under a directory'''

    def __init__(self, dir):
        '''define the interface components'''
        self.baseDir = dir
        self.db = {}
        self.mtime = -1
        self.file = ''
        self.discover()
        
    def discover(self):
        '''walk the directory tree looking for treasures'''
        if not os.path.exists(self.baseDir):
            return      # cannot find this item
        now = time.time()
        time_window = now - TIME_WINDOWS_SECS
        for (dirpath, dirnames, filenames) in os.walk(self.baseDir):
            if os.path.split(os.path.abspath(dirpath))[-1] in SKIP_DIRS:
                continue    # weed out unwanted directories
            if len(filenames) == 0:
                continue    # no files in this directory
            absdir = os.path.abspath(dirpath)
            for item in filenames:
                ext = string.lower(os.path.splitext(item)[-1])
                if not ext in KEEP_EXTS:
                    continue    # only look at certain files
                full = os.path.join(dirpath, item)
                mtime = os.path.getmtime(os.path.join(absdir, item))
                if mtime < time_window:
                    continue    # only examine recent files
                self.db[full] = mtime
                if mtime > self.mtime:
                    self.mtime = mtime
                    self.file = full


def ts2text(ts):
    '''convert a floating-point timestamp into text'''
    return time.strftime(TIMESTAMP_FORMAT, time.localtime(ts))


if __name__ == '__main__':
    first = dirWatch(BASE_DIR)
    ts = ts2text(first.mtime)
    #print len(first.db), ts, first.file
    for item in first.db:
        print ts2text(first.db[item]), item
