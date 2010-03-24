#!/bin/tcsh
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
#
# chkconfig: - 98 98
# description: 32ID USAXS WWW page update script
#
# processname: usaxs_update

setenv SCRIPT_DIR /home/joule/USAXS/code/livedata
setenv SCRIPT  ${SCRIPT_DIR}/main.tcl
setenv LOGFILE ${SCRIPT_DIR}/log.txt
setenv PIDFILE ${SCRIPT_DIR}/pid.txt

switch ($1)
  case "start":
        cd ${SCRIPT_DIR}
        ${SCRIPT} >>& ${LOGFILE} &
        setenv PID $!
        /bin/echo ${PID} >! ${PIDFILE}
        /bin/echo "started ${PID}: ${SCRIPT}"
        breaksw
  case "stop":
        cd ${SCRIPT_DIR}
        setenv PID `/bin/cat ${PIDFILE}`
        /bin/ps ${PID} >! /dev/null
        setenv NOT_EXISTS $?
        if (${NOT_EXISTS}) then
             /bin/echo "not running ${PID}: ${SCRIPT}"
        else
             kill ${PID}
             /bin/echo "stopped ${PID}: ${SCRIPT}"
        endif
        breaksw
  case "restart":
        $0 stop
        $0 start
        breaksw
  default:
        /bin/echo "Usage: $0 {start|stop|restart}"
        breaksw
endsw
