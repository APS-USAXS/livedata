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
import datetime


# general use
WWW_SERVER_ROOT = "usaxs@www-i.xray.aps.anl.gov"
LIVEDATA_DIR = "www/livedata"
SERVER_WWW_HOMEDIR = WWW_SERVER_ROOT + ":~"
SERVER_WWW_LIVEDATA = os.path.join(SERVER_WWW_HOMEDIR, LIVEDATA_DIR)
LOCAL_DATA_DIR = "/data"
LOCAL_USAXS_DATA__DIR = LOCAL_DATA_DIR + "/USAXS_data"
LOCAL_WWW = LOCAL_DATA_DIR + "/www"
LOCAL_WWW_LIVEDATA = os.path.join(LOCAL_DATA_DIR, LIVEDATA_DIR)
SCP_TIMEOUT_S = 30

SCP = "/usr/bin/scp"
RSYNC = "/usr/bin/rsync"


def scpToWebServer_Demonstrate(sourceFile, targetFile = ""):
    '''
    Demonstrate a copy from the local source file to the WWW server using scp BUT DO NOT DO IT
    ...
    ... this is useful for code development only...
    ...

    @param sourceFile: file in local file space *relative* to /data/www/livedata
    @param targetFile: destination file (default is same path as sourceFile)
    @return: None
    '''
    return scpToWebServer(sourceFile, targetFile, demo = True)


def scpToWebServer(sourceFile, targetFile = "", demo = False):
    '''
    Copy the local source file to the WWW server using scp.

    @param sourceFile: file in local file space relative to /data/www/livedata
    @param targetFile: destination file (default is same path as sourceFile)
    @param demo: If True, don't do the copy, just print the command
    @return: a tuple (stdoutdata,  stderrdata) -or- None (if demo=False)
    '''
    import pvwatch
    # Can we replace scpToWebServer() with Python package capabilities?
    #  No major improvement.
    # see: http://stackoverflow.com/questions/250283/how-to-scp-in-python
    # see: http://stackoverflow.com/questions/68335/how-do-i-copy-a-file-to-a-remote-server-in-python-using-scp-or-ssh?lq=1
    if not os.path.exists(sourceFile):
        raise Exception("Local file not found: " + sourceFile)
    if len(targetFile) == 0:
        targetFile = sourceFile
    destinationName = os.path.join(SERVER_WWW_LIVEDATA, targetFile)
    command = "%s -p %s %s" % (SCP, sourceFile, destinationName)
    if demo:
        print command
        return None
    else:
        lex = shlex.split(command)
        pvwatch.debugging_diagnostic(211)
        timeout_time = pvwatch.getTime() + datetime.timedelta(seconds=SCP_TIMEOUT_S)
        p = subprocess.Popen(lex)
        pvwatch.debugging_diagnostic(212)
        finished = False
        while pvwatch.getTime() < timeout_time and not finished:
            code = p.poll()
            if code is not None:
                finished = True
        result = p.communicate(None)
        if not finished or code != 0:
            msg = {True: 'problem', False: 'timeout'}[finished]
            msg += ': command `%s` returned code=%d' % (command, code)
            msg += '\nSTDOUT=%s\nSTDERR=%s' % (str(result[0]), str(result[1]))
            pvwatch.logMessage(msg)
        return result


def execute_command(command):
    '''
    execute the specified shell command

    @return: a tuple (stdoutdata,  stderrdata)
    '''
    # run the command but gobble up stdout (make it less noisy)
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    #p.wait()
    return p.communicate(None)


if __name__ == '__main__':
    scpToWebServer("wwwServerTransfers.py")
    scpToWebServer_Demonstrate("wwwServerTransfers.py")
    try:
        scpToWebServer("wally.txt")
    except:
        print sys.exc_info()[1]
    scpToWebServer("wwwServerTransfers.py", "wally.txt")
    scpToWebServer_Demonstrate("wwwServerTransfers.py", "wally.txt")
