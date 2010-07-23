#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   manage file transfers with the USAXS account on the XSD WWW server
'''


import os, sys
import subprocess
import shlex
import shutil


# general use
WWW_SERVER_ROOT = "usaxs@usaxs.xor.aps.anl.gov"
LIVEDATA_DIR = "www/livedata"
SERVER_WWW_HOMEDIR = WWW_SERVER_ROOT + ":~"
SERVER_WWW_LIVEDATA = os.path.join(SERVER_WWW_HOMEDIR, LIVEDATA_DIR)
LOCAL_DATA_DIR = "/data"
LOCAL_USAXS_DATA__DIR = LOCAL_DATA_DIR + "/USAXS_data"
LOCAL_WWW = LOCAL_DATA_DIR + "/www"
LOCAL_WWW_LIVEDATA = os.path.join(LOCAL_DATA_DIR, LIVEDATA_DIR)

SCP = "/usr/bin/scp"
RSYNC = "/usr/bin/rsync"


def scpToWebServer_Demonstrate(sourceFile, targetFile = ""):
    '''
    Demonstrate a copy the local source file to the WWW server using scp BUT DON"T DO IT
    ...
    ... this is useful for code development only...
    ...
    @param sourceFile: file in local file space *relative* to /data/www/livedata
    @param targetFile: destination file (default is same path as sourceFile)
    '''
    if not os.path.exists(sourceFile):
        raise Exception("Local file not found: " + sourceFile)
    if len(targetFile) == 0:
        targetFile = sourceFile
    destinationName = os.path.join(SERVER_WWW_LIVEDATA, targetFile)
    command = "%s -p %s %s" % (SCP, sourceFile, destinationName)
    print command


def scpToWebServer(sourceFile, targetFile = ""):
    '''
    copy the local source file to the WWW server using scp
    @param sourceFile: file in local file space relative to /data/www/livedata
    @param targetFile: destination file (default is same path as sourceFile)
    '''
    if not os.path.exists(sourceFile):
        raise Exception("Local file not found: " + sourceFile)
    if len(targetFile) == 0:
        targetFile = sourceFile
    destinationName = os.path.join(SERVER_WWW_LIVEDATA, targetFile)
    command = "%s -p %s %s" % (SCP, sourceFile, destinationName)
    lex = shlex.split(command)
    p = subprocess.Popen(lex)
    p.wait()


def execute_command(command):
    '''
    execute the specified command
    '''
    # run the command but gobble up stdout (make it less noisy)
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    p.wait()


if __name__ == '__main__':
    scpToWebServer("wwwServerTransfers.py")
    scpToWebServer_Demonstrate("wwwServerTransfers.py")
    try:
        scpToWebServer("wally.txt")
    except:
        print sys.exc_info()[1]
    scpToWebServer("wwwServerTransfers.py", "wally.txt")
    scpToWebServer_Demonstrate("wwwServerTransfers.py", "wally.txt")
