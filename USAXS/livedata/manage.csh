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

setenv SCRIPT_DIR	 /home/beams/S15USAXS/Documents/eclipse/USAXS/livedata
setenv MANAGE		 ${SCRIPT_DIR}/manage.csh
setenv PLOTICUS_PREFABS  /home/beams/S15USAXS/Documents/ploticus/pl241src/prefabs
setenv WWW_DIR		 /data/www/livedata
setenv SCRIPT		 ${SCRIPT_DIR}/pvwatch.py
setenv LOGFILE		 ${WWW_DIR}/log.txt
setenv PIDFILE		 ${WWW_DIR}/pid.txt
setenv COUNTERFILE	 ${WWW_DIR}/counter.txt
setenv PYTHON		 /APSshare/epd/rh6-x86_64/bin/python
setenv CAGET		 /APSshare/epics/extensions-base/3.14.12.3-ext1/bin/linux-x86_64/caget

switch ($1)
  case "start":
       cd ${SCRIPT_DIR}
       ${PYTHON} ${SCRIPT} >>& ${LOGFILE} &
       setenv PID $!
       /bin/echo ${PID} >! ${PIDFILE}
       /bin/echo "# `/bin/date` started ${PID}: ${SCRIPT}"
       /bin/echo -5 >! ${COUNTERFILE}
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
            /bin/echo "# not running ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
       else
            kill ${PID}
            /bin/echo "# `/bin/date` stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
            /bin/echo "# `/bin/date` stopped ${PID}: ${SCRIPT}"
       endif
       # the python code starts a 2nd PID which also needs to be stopped
       setenv PID `expr "${pidlist}" : '[0-9]*\( [0-9]*\)'`
       /bin/ps ${PID} >! /dev/null
       setenv NOT_EXISTS $?
       if (${NOT_EXISTS}) then
            /bin/echo "# `/bin/date` not running ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
       else
            if (${PID} != "") then
		 kill ${PID}
 		 /bin/echo "# `/bin/date` stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
 		 /bin/echo "# `/bin/date` stopped ${PID}: ${SCRIPT}"
	    endif
       endif
       /bin/echo "# `/bin/date` pvWatch mainLoopCounter: `${CAGET} 15iddLAX:long20`"  >>& ${LOGFILE} &
       /bin/echo "# `/bin/date` pvWatch phase: `${CAGET} 15iddLAX:long18`"  >>& ${LOGFILE} &
       breaksw
  case "restart":
       $0 stop
       $0 start
       breaksw
  case "checkup":
       #=====================
       # call peridiocally (every 5 minutes) to see if livedata is running
       #=====================
       #	field	       allowed values
       #      -----	     --------------
       #      minute	     0-59
       #      hour	     0-23
       #      day of month   1-31
       #      month	     1-12 (or names, see below)
       #      day of week    0-7 (0 or 7 is Sun, or use names)
       #
       # */5 * * * * /home/beams/S15USAXS/Documents/eclipse/USAXS/livedata/manage.csh checkup 2>&1 /dev/null
       #
       set pid = `/bin/cat ${PIDFILE}`
       setenv RESPONSE `ps -p ${pid} -o comm=`
       if (${RESPONSE} != "python") then
          echo "# `/bin/date` could not identify running process ${pid}, restarting" >>& ${LOGFILE}
	  # swallow up any console output
          echo `${MANAGE} restart` >& /dev/null
       else
 	  # look to see if the process has stalled, then restart it
	  set counter = `${CAGET} -t 15iddLAX:long20`
	  set last_counter = `/bin/cat ${COUNTERFILE}`
          #echo "# counter = ${counter}   last_counter ${last_counter}" >>& ${LOGFILE}
	  if ("${counter}" == "${last_counter}") then
 	     echo "# `/bin/date` process ${pid} appears stalled, restarting" >>& ${LOGFILE}
	     # swallow up any console output
 	     echo `${MANAGE} restart` >& /dev/null
 	  else
	     /bin/echo ${counter} >! ${COUNTERFILE}
	  endif
       endif
       breaksw
  default:
       /bin/echo "Usage: $0 {start|stop|restart|checkup}"
       breaksw
endsw
