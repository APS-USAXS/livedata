#!/usr/bin/env python

'''
manage file transfers with the USAXS account on the XSD WWW server
'''


import os, sys
import subprocess
import shlex
import datetime
import paramiko
import socket
from scp import SCPClient, report_scp_progress, SCPException


# general use
WWW_SERVER = 'www-i.xray.aps.anl.gov'
WWW_SERVER_USER = 'webusaxs'
WWW_SERVER_ROOT = WWW_SERVER_USER + '@' + WWW_SERVER
LIVEDATA_DIR = "www/livedata"
SERVER_WWW_HOMEDIR = WWW_SERVER_ROOT + ":~"
SERVER_WWW_LIVEDATA = os.path.join(SERVER_WWW_HOMEDIR, LIVEDATA_DIR)

LOCAL_DATA_DIR = "/share1"
LOCAL_WWW = os.path.join(LOCAL_DATA_DIR, 'local_livedata')
LOCAL_WWW_LIVEDATA = os.path.join(LOCAL_DATA_DIR, LIVEDATA_DIR)

LOCAL_USAXS_DATA__DIR = LOCAL_DATA_DIR + "/USAXS_data"

RSYNC = "/usr/bin/rsync"
SCP = "/usr/bin/scp"
SCP_TIMEOUT_S = 30
RETRY_COUNT = 3


class WwwServerScpException(Exception): pass


def scpToWebServer(sourceFile, targetFile = "", demo = False):
    '''
    Copy the local source file to the WWW server using scp.

    @param sourceFile: file in local file space relative to /share1/local_livedata
    @param targetFile: destination file (default is same path as sourceFile)
    @param demo: If True, don't do the copy, just print the command
    @return: a tuple (stdoutdata,  stderrdata) -or- None (if demo=False)
    '''
    if not os.path.exists(sourceFile):
        raise Exception("Local file not found: " + sourceFile)
    if len(targetFile) == 0:
        targetFile = sourceFile
    destinationName = os.path.join(SERVER_WWW_LIVEDATA, targetFile)
    if demo:
        print "%s -p %s %s" % (SCP, sourceFile, destinationName)
        return None

    # TODO: handle exceptions
    ssh = createSSHClient(WWW_SERVER, user=WWW_SERVER_USER)
    report = None
    #report = report_scp_progress    # debugging
    scp = SCPClient(ssh.get_transport(), progress=report)
    for _retry in range(RETRY_COUNT):
        try:
            scp.put(sourceFile, remote_path=LIVEDATA_DIR)
            return
        except (SCPException, SSHException, socket.error), exc:
            print '# retry %d: %e' % ((_retry+1), exc)
    msg = 'tried %d times: scp %s %s' % (RETRY_COUNT, sourceFile, targetFile)
    WwwServerScpException(msg)


def scpToWebServer_Demonstrate(sourceFile, targetFile = ""):
    '''
    Demonstrate a copy from the local source file to the WWW server using scp BUT DO NOT DO IT
    ...
    ... this is useful for code development only...
    ...

    @param sourceFile: file in local file space *relative* to /share1/local_livedata
    @param targetFile: destination file (default is same path as sourceFile)
    @return: None
    '''
    return scpToWebServer(sourceFile, targetFile, demo = True)


def scpToWebServer_subprocess(sourceFile, targetFile = "", demo = False):
    '''
    Copy the local source file to the WWW server using scp.

    @param sourceFile: file in local file space relative to /share1/local_livedata
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
        timeout_time = pvwatch.getTime() + datetime.timedelta(seconds=SCP_TIMEOUT_S)
        p = subprocess.Popen(lex)
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


def createSSHClient(server, port=None, user=None, password=None):
    '''scp over a paramiko transport'''
    # see: http://stackoverflow.com/questions/250283/how-to-scp-in-python
    # TODO: handle exceptions
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #client.connect(server, port, user, password)
    client.connect(server, username=user)
    return client


if __name__ == '__main__':
    scpToWebServer("wwwServerTransfers.py")
    scpToWebServer_Demonstrate("wwwServerTransfers.py")
    try:
        scpToWebServer("wally.txt")
    except:
        print sys.exc_info()[1]
    scpToWebServer("wwwServerTransfers.py", "wally.txt")
    scpToWebServer_Demonstrate("wwwServerTransfers.py", "wally.txt")


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
