#!/bin/bash

# crawl directories for SPEC data files and build default plots for all scans

#--------------------------------------------------------------------
# This script could be called from cron such as
#
#   # every five minutes (generates no output from outer script)
#   0-59/5 * * * *  $HOME/Documents/eclipse/USAXS/livedata/buildSpecPlots.sh
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# tips for when too many process have been started:
# kill -9 `psg bash | awk '/buildSpecPlots.sh/ {print $2}' -`
# kill -9 `psg python | awk '/specplotsAllScans.py/ {print $2}' -`
#--------------------------------------------------------------------

CODE_DIR=/home/beams/USAXS/Documents/eclipse/USAXS/livedata
PROGRAM=$CODE_DIR/specplotsAllScans.py
LOGFILE=/share1/local_livedata/specplots/specplots.log
#PYTHON=/APSshare/epd/rh6-x86_64/bin/python
PYTHON=/APSshare/anaconda/x86_64/bin/python
HDF5_DISABLE_VERSION_CHECK=2

#
# change the SPEC_DATA_PATTERN periodically to reduce the search time
# this is very important, for example, just this one directory:
#   /data/USAXS_data/2013-1*/*.dat  takes about a minute to run
#
#SPEC_DATA_PATTERN=/data/USAXS_data/2010-04/*.dat
#SPEC_DATA_PATTERN=/data/USAXS_data/201*-*/*.dat
#SPEC_DATA_PATTERN=/data/USAXS_data/2013-1*/*.dat
#SPEC_DATA_PATTERN=/data/USAXS_data/2014-*/*.dat
#SPEC_DATA_PATTERN=/share1/USAXS_data/2015-*/*.dat
#SPEC_DATA_PATTERN=/share1/USAXS_data/2016-*/*.dat
SPEC_DATA_PATTERN=/share1/USAXS_data/2017-*/*.dat

#export PLOTICUS_BASE=/home/beams/USAXS/Documents/ploticus/pl241src
#export PLOTICUS_PREFABS=$PLOTICUS_BASE/prefabs

cd $CODE_DIR
echo "#= $$ --Start--- `/bin/date`" >> $LOGFILE 2>&1

filelist=`/bin/ls -1 $SPEC_DATA_PATTERN`
# for item in $filelist; 
# 	do
# 	# echo $item >> $LOGFILE 2>&1;
# 	$PYTHON $PROGRAM $item >> $LOGFILE 2>&1;
# done
$PYTHON $PROGRAM $filelist >> $LOGFILE 2>&1;
echo "#= $$ --Done---------------------------------- `/bin/date`" >> $LOGFILE 2>&1


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
