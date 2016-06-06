#!/bin/tcsh
#
# chkconfig: - 98 98
# description: 9-ID USAXS WWW page update script
#
# processname: usaxs_update

setenv SCRIPT_DIR	 /home/beams/USAXS/Documents/eclipse/USAXS/livedata
setenv MANAGE		 ${SCRIPT_DIR}/manage.csh
setenv PLOTICUS_PREFABS  /home/beams/USAXS/Documents/ploticus/pl241src/prefabs
setenv WWW_DIR		 /share1/local_livedata
setenv SCRIPT		 ${SCRIPT_DIR}/pvwatch.py
setenv LOGFILE		 ${WWW_DIR}/log.txt
setenv PIDFILE		 ${WWW_DIR}/pid.txt
setenv COUNTERFILE	 ${WWW_DIR}/counter.txt
setenv PYTHON		 /APSshare/anaconda/x86_64/bin/python
setenv CAGET		 /APSshare/epics/extensions-base/3.14.12.3-ext1/bin/linux-x86_64/caget
setenv PVWATCH_PHASE_PV  9idcLAX:long18
setenv LOOP_COUNTER_PV   9idcLAX:long20
setenv HDF5_DISABLE_VERSION_CHECK 2

# a little bit of protection here ...
setenv HOSTNAME `/bin/hostname`
if ("${HOSTNAME}" != "usaxscontrol.xray.aps.anl.gov") then
            /bin/echo "hostname = ${HOSTNAME} : not intended to run on this host"
       exit
endif


switch ($1)
  case "start":
       cd ${SCRIPT_DIR}
       /bin/echo "# [$0 `/bin/date`] start ======================================================"  >>& ${LOGFILE}
       ${PYTHON} ${SCRIPT} >>& ${LOGFILE} &
       setenv PID $!
       /bin/echo ${PID} >! ${PIDFILE}
       /bin/echo "# [$0 `/bin/date`] started ${PID}: ${SCRIPT}"
       /bin/echo -5 >! ${COUNTERFILE}
       breaksw

  case "stop":
       cd ${SCRIPT_DIR}
       setenv PID `/bin/cat ${PIDFILE}`
       # get the full list of PID children
       # this line browses pstree and strips non-numbers
       set pidlist=`pstree -p $PID | tr -c "[:digit:]"  " " `
       /bin/ps ${PID} >! /dev/null
       setenv NOT_EXISTS $?
       if (${NOT_EXISTS}) then
            /bin/echo "# not running ${PID}: ${SCRIPT}" >>& ${LOGFILE}
       else
            kill ${PID}
            /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE}
            /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}"
       endif
       #?archaic?#  # the python code starts a 2nd PID which also needs to be stopped
       #?archaic?#  setenv PID `expr "${pidlist}" : '[0-9]*\( [0-9]*\)'`
       #?archaic?#  /bin/ps ${PID} >! /dev/null
       #?archaic?#  setenv NOT_EXISTS $?
       #?archaic?#  if (${NOT_EXISTS}) then
       #?archaic?#	 /bin/echo "# [$0 `/bin/date`] not running ${PID}: ${SCRIPT}" >>& ${LOGFILE}
       #?archaic?#  else
       #?archaic?#	 if (${PID} != "") then
       #?archaic?#	      kill ${PID}
       #?archaic?#	      /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE}
       #?archaic?#	      /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}"
       #?archaic?#	 endif
       #?archaic?#  endif
       #/bin/echo "# [$0 `/bin/date`] pvWatch mainLoopCounter: `${CAGET} ${LOOP_COUNTER_PV}`"  >>& ${LOGFILE}
       #/bin/echo "# [$0 `/bin/date`] pvWatch phase: `${CAGET} ${PVWATCH_PHASE_PV}`"  >>& ${LOGFILE}
       /bin/echo "# [$0 `/bin/date`] stop ======================================================"  >>& ${LOGFILE}
       breaksw

  case "restart":
       $0 stop
       $0 start
       breaksw

  case "checkup":
       #=====================
       # call periodically (every 5 minutes) to see if livedata is running
       #=====================
       #	field	       allowed values
       #      -----	     --------------
       #      minute	     0-59
       #      hour	     0-23
       #      day of month   1-31
       #      month	     1-12 (or names, see below)
       #      day of week    0-7 (0 or 7 is Sun, or use names)
       #
       # build: http://usaxs.xray.aps.anl.gov/livedata/
       # */5 * * * * /home/beams/USAXS/Documents/eclipse/USAXS/livedata/manage.csh checkup 2>&1 /dev/null
       #

       #2015-02-04,prj: removed, sends nuisance emails
       ## 2013-10-25,prj: new cleanup part, until pvwatch.py starts getting it right again
       #/bin/rm -f /tmp/tmp*.p*

       set pid = `/bin/cat ${PIDFILE}`
       setenv RESPONSE `ps -p ${pid} -o comm=`
       if (${RESPONSE} != "python") then
          echo "# [$0 `/bin/date`] could not identify running process ${pid}, restarting" >>& ${LOGFILE}
	      # swallow up any console output
          echo `${MANAGE} restart` >& /dev/null
       else
 	      # look to see if the process has stalled, then restart it
	      #set counter = `${CAGET} -t ${LOOP_COUNTER_PV}`
 	      #echo "# [$0 `/bin/date`] checkup pid=${pid}, counter=${counter}" >>& ${LOGFILE}
	      #set last_counter = `/bin/cat ${COUNTERFILE}`
	      #if ("${counter}" == "${last_counter}") then
 	      #   echo "# [$0 `/bin/date`] process ${pid} appears stalled, restarting" >>& ${LOGFILE}
	      #   # swallow up any console output
 	      #   echo `${MANAGE} restart` >& /dev/null
 	      #else
	      #   /bin/echo ${counter} >! ${COUNTERFILE}
	      #endif
       endif
       breaksw

  default:
       /bin/echo "Usage: $0 {start|stop|restart|checkup}"
       breaksw

endsw

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
