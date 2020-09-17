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
# NOTE: code is still python 2.7
#PYTHON=/APSshare/epd/rh6-x86_64/bin/python
PYTHON=/APSshare/anaconda/x86_64/bin/python
HDF5_DISABLE_VERSION_CHECK=2

cd $CODE_DIR
echo "#= $$ --Start--- `/bin/date`" >> $LOGFILE 2>&1

# 2019-07-09, prj: look at scan logs and build the list
filelist=`$PYTHON ./recent_spec_data_files.py`

$PYTHON $PROGRAM $filelist >> $LOGFILE 2>&1;
echo "#= $$ --Done---------------------------------- `/bin/date`" >> $LOGFILE 2>&1
