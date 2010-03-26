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
setenv SCRIPT  ${SCRIPT_DIR}/pvwatch.py
setenv LOGFILE ${SCRIPT_DIR}/log.txt
setenv PIDFILE ${SCRIPT_DIR}/pid.txt
setenv PYTHON  /APSshare/bin/python


# what about trolling this for the two PIDs to kill?
#pstree -p `cat pid.txt`
#python(12646)\u2500\u2500\u2500python(12660)\u2500\u252c\u2500{python}(12661)
#			      \u251c\u2500{python}(12662)
#			      \u251c\u2500{python}(12663)
#			      \u251c\u2500{python}(12666)
#			      \u251c\u2500{python}(12667)
#			      \u251c\u2500{python}(12668)
#			      \u251c\u2500{python}(12669)
#			      \u251c\u2500{python}(12670)
#			      \u251c\u2500{python}(12671)
#			      \u251c\u2500{python}(12672)
#			      \u251c\u2500{python}(12673)
#			      \u251c\u2500{python}(12674)
#			      \u251c\u2500{python}(12675)
#			      \u251c\u2500{python}(12676)
#			      \u2514\u2500{python}(12677)
# kill 12646 12660


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
