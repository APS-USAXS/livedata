#!/bin/bash
########### SVN repository information ###################
# $Date: 2010-03-27 11:00:35 -0500 (Sat, 27 Mar 2010) $
# $Author: jemian $
# $Revision: 259 $
# $URL: https://subversion.xor.aps.anl.gov/small_angle/USAXS/livedata/manage.csh $
# $Id: manage.csh 259 2010-03-27 16:00:35Z jemian $
########### SVN repository information ###################

WORKING_DIR=/home/joule/USAXS/code/livedata
LOGFILE=$WORKING_DIR/specplots.log
SPEC_DATA_PATTERN=/share1/USAXS_data/2010-04/*.dat

export PLOTICUS_BASE=/home/joule/USAXS/code/pl233src
export PLOTICUS_PREFABS=/home/joule/USAXS/code/pl233src/prefabs

/bin/date >> $LOGFILE 2>&1;
cd $WORKING_DIR

filelist=`/bin/ls -1 $SPEC_DATA_PATTERN`
for item in $filelist; 
  do
  echo $item >> $LOGFILE 2>&1;
  $WORKING_DIR/plotAllSpecFileScans.py $item >> $LOGFILE 2>&1;
done
