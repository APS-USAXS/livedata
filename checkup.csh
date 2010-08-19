#!/bin/tcsh
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

# purpose: ensure the livedata WWW page software is running
# call from cron job periodically

setenv PIDFILE /data/www/livedata/pid.txt
setenv MANAGE /home/beams/S15USAXS/Documents/eclipse/USAXS/livedata/manage.csh
setenv PID `/bin/cat ${PIDFILE}`

setenv RESPONSE `ps -p ${PID} -o comm=`
echo $RESPONSE

if (${RESPONSE} != "python") then
   ${MANAGE} restart >! /dev/null
endif
