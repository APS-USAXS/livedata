#!/bin/bash
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

# script to crawl directories for SPEC data files and build default plots for all scans
# This script could be called from cron such as
#
#		# every five minutes
#		0-59/5 * * * *  /home/beams/S15USAXS/Documents/eclipse/USAXS/livedata/buildSpecPlots.sh

CODE_DIR=/home/beams/S15USAXS/Documents/eclipse/USAXS/livedata
PROGRAM=$CODE_DIR/specplotsAllScans
LOGFILE=/data/www/livedata/specplots/specplots.log

#
# change the SPEC_DATA_PATTERN periodically to reduce the search time
#
#SPEC_DATA_PATTERN=/data/USAXS_data/2010-04/*.dat
SPEC_DATA_PATTERN=/data/USAXS_data/201*-*/*.dat

export PLOTICUS_BASE=/home/beams/S15USAXS/Documents/ploticus/pl241src
export PLOTICUS_PREFABS=$PLOTICUS_BASE/prefabs

cd $CODE_DIR
echo "#=-------------" >> $LOGFILE 2>&1
/bin/date >> $LOGFILE 2>&1

filelist=`/bin/ls -1 $SPEC_DATA_PATTERN`
for item in $filelist; 
	do
	# echo $item >> $LOGFILE 2>&1;
	$PROGRAM $item >> $LOGFILE 2>&1;
done
