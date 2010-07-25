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
# description: 15ID USAXS WWW page update script
#
# processname: usaxs_update

#@TODO: needs to be converted to 15ID-D

setenv SCRIPT_DIR /home/beams/S15USAXS/Documents/eclipse/USAXS/livedata
setenv PLOTICUS_PREFABS /home/beams/S15USAXS/Documents/ploticus/pl241src/prefabs
setenv WWW_DIR    /data/www/livedata
setenv SCRIPT  ${SCRIPT_DIR}/pvwatch.py
setenv LOGFILE ${WWW_DIR}/log.txt
setenv PIDFILE ${WWW_DIR}/pid.txt
setenv PYTHON  /APSshare/bin/python

switch ($1)
  case "start":
       cd ${SCRIPT_DIR}
       ${PYTHON} ${SCRIPT} >>& ${LOGFILE} &
       setenv PID $!
       /bin/echo ${PID} >! ${PIDFILE}
       /bin/echo "started ${PID}: ${SCRIPT}"
       breaksw
  case "stop":
       cd ${SCRIPT_DIR}
       setenv PID `/bin/cat ${PIDFILE}`
       # get the full list of PID children
       # this line trolls pstree and strips non-numbers
       set pidlist=`pstree -p $PID | tr -c "[:digit:]"  " " `
       /bin/ps ${PID} >! /dev/null
       setenv NOT_EXISTS $?
       if (${NOT_EXISTS}) then
            /bin/echo "not running ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
       else
            kill ${PID}
            /bin/echo "stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
            /bin/echo "stopped ${PID}: ${SCRIPT}"
       endif
       # the python code starts a 2nd PID which also needs to be stopped
       setenv PID `expr "${pidlist}" : '[0-9]*\( [0-9]*\)'`
       /bin/ps ${PID} >! /dev/null
       setenv NOT_EXISTS $?
       if (${NOT_EXISTS}) then
            /bin/echo "not running ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
       else
            kill ${PID}
            /bin/echo "stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
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
