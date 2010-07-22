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
   
   TODO: this is an incomplete project, it seems
'''

import os
import string
#import sys
import time
import localConfig      # definitions for 15ID


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
        '''
        walk the directory tree looking for new treasures
        @TODO: this algorithm is not very efficient
            It keeps regenerating files even when the source has not changed.
        '''
        if not os.path.exists(self.baseDir):
            return      # cannot find this item
        now = time.time()
        time_window = now - localConfig.TIME_WINDOWS_SECS
        for (dirpath, dirnames, filenames) in os.walk(self.baseDir):
            tail = os.path.split(os.path.abspath(dirpath))[-1]
            if tail in localConfig.SKIP_DIRS:
                continue    # weed out unwanted directories
            if len(filenames) == 0:
                continue    # no files in this directory
            absdir = os.path.abspath(dirpath)
            for item in filenames:
                ext = string.lower(os.path.splitext(item)[-1])
                if not ext in localConfig.KEEP_EXTS:
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
    return time.strftime(localConfig.TIMESTAMP_FORMAT, time.localtime(ts))


if __name__ == '__main__':
    first = dirWatch(localConfig.BASE_DIR)
    ts = ts2text(first.mtime)
    keys = first.db.keys()
    keys.sort()
    #print len(first.db), ts, first.file
    for item in keys:
        print ts2text(first.db[item]), item
