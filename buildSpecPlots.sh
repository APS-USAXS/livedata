#!/bin/bash
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

WORKING_DIR=/home/beams/S15USAXS/Documents/eclipse/USAXS/livedata
LOGFILE=$WORKING_DIR/www/specplots.log
#SPEC_DATA_PATTERN=/data/USAXS_data/20*-*/*.dat
SPEC_DATA_PATTERN=/data/USAXS_data/2010-04/*.dat

export PLOTICUS_BASE=/home/beams/S15USAXS/Documents/ploticus/pl241src
export PLOTICUS_PREFABS=$PLOTICUS_BASE/prefabs

cd $WORKING_DIR
echo "#=-------------" >> $LOGFILE 2>&1
/bin/date >> $LOGFILE 2>&1

filelist=`/bin/ls -1 $SPEC_DATA_PATTERN`
for item in $filelist; 
  do
  # echo $item >> $LOGFILE 2>&1;
  $WORKING_DIR/plotAllSpecFileScans.py $item >> $LOGFILE 2>&1;
done
