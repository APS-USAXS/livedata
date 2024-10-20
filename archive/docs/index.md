# `livedata` source code

**Contents**
- [`livedata` source code](#livedata-source-code)
  - [Major Code Blocks](#major-code-blocks)
    - [NOTE](#note)
  - [List of files](#list-of-files)


## Major Code Blocks

    Makefile
        --- calls starts/stops/restarts manage.csh

    manage.csh
        --- starts/stops/restarts pvwatch.py
        --- sysAdmins could point to this from /etc/init.d or similar

    pvwatch.py
        --- *** this is the main code of this "package" ***
        --- uses these resources
            pvlist.xml
            pvConnect.py
            livedata.xsl
            localConfig.py
            prjPySpec.py
            raw-table.xsl
            specplot.py
            wwwServerTransfers.py
        --- and generates files in /data/www/livedata
            index.html
            livedata.png
            raw-report.html
            report.xml
            specmacro.txt
        --- copies these to the XSD WWW server as they are generated

    buildSpecPlots.sh
        --- uses these resources
            specplotsAllScans.py
            specplot.py
        --- and generates files and subdirs in
            /data/www/livedata/specplots
        --- rsyncs these to the XSD WWW server as they are generated
    This script could be called from a cron job every 5 minutes or so.  Not any more frequent, though.

    dirWatch.py
        --- will probably go away - ignore it

### NOTE

While many of the Python routines have code that executes when called
directly from the command line, don\'t do this unless you are CERTAIN of
what will happen. Some routines change the local WWW dir and some even
push files to the XSD WWW server.

## List of files

file | remarks
--- | ---
__init__.py | tells Python this directory is a \"package\"
buildSpecPlots.sh | script to crawl directories for SPEC data files and build default plots for all scans
dirWatch.py | code under development
livedata.xsl | XSLT transform to build index.html from XML data
localConfig.py | global Python variables for this package
Makefile | starts/stops the manage.csh script
manage.csh | sysAdmin script to start/stop pvwatch.py
plot.py | plots last $n$ USAXS scans from one SPEC data file
prjPySpec.py | reads SPEC data files
pvConnect.py | EPICS PV connection management
pvlist.xml | list of EPICS process variables to be monitored/reported
pvlist.xsl | convenience XSLT transform to view pvlist.xml in a browser
pvwatch.py | watches PVs, writes reports, makes livedata page content
raw-table.xsl | XSLT transform to build raw-report.html from XML data
README | basic documentation for code developers
specplot.py | default plot of one scan in one SPEC data file
specplotsAllScans.py | default plots of all scans in one SPEC data file
www/ | soft link to local WWW root directory (/data/www)
wwwServerTransfers.py | common code to scp files from usaxscontrol2.cars to usaxs.xor
