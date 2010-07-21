#!/bin/bash
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

#@TODO: needs to be converted to 15ID-D

WORKING_DIR=/home/joule/USAXS/code/livedata
LOGFILE=$WORKING_DIR/specplots.log
#SPEC_DATA_PATTERN=/share1/USAXS_data/20*-*/*.dat
SPEC_DATA_PATTERN=/share1/USAXS_data/2010-04/*.dat

#@TODO: needs ploticus

export PLOTICUS_BASE=/home/joule/USAXS/code/pl233src
export PLOTICUS_PREFABS=/home/joule/USAXS/code/pl233src/prefabs

cd $WORKING_DIR
echo "#!-------------" >> $LOGFILE 2>&1
/bin/date >> $LOGFILE 2>&1

filelist=`/bin/ls -1 $SPEC_DATA_PATTERN`
for item in $filelist; 
  do
  echo $item >> $LOGFILE 2>&1;
  $WORKING_DIR/plotAllSpecFileScans.py $item >> $LOGFILE 2>&1;
done
