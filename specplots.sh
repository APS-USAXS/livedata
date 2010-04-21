#!/bin/bash
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

WORKING_DIR=/home/joule/USAXS/code/livedata
LOGFILE=$WORKING_DIR/specplots.log
#SPEC_DATA_PATTERN=/share1/USAXS_data/20*-*/*.dat
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
