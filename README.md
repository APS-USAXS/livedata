# README for USAXS `livedata`

Manage the display of live USAXS data at: https://usaxslive.xray.aps.anl.gov/

The main code here is *pvwatch.py*.  It monitors EPICS PVs
(described in *pvlist.xml*) and writes files in the local
WWW server directory.  It can be started and stopped by
the `Makefile` (for manual control) or the `manage.csh` script
for automated startup in a cron task, `/etc/init.d`, or similar.

Another code module, *buildSpecPlots.sh*, crawls a set of
subdirectories, looking for data files and plotting
all scans using defaults (last column *vs.* first column).

NOTE: [v1 code documentation](archive/docs/index.md)
