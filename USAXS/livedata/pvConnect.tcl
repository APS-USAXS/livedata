#! /bin/sh
#
# the next line restarts using OAG Tcl shell oagtclsh \
   exec oagtclsh "$0" ${1+"$@"}

########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

# 2009-03-19,PRJ:  On APS Linux systems, 
#  the OAG TCL toolkit is installed under /usr/local/oag
lappend auto_path /usr/local/oag/apps/lib/Linux

# some older oagtclsh versions do not need this
# fail silently (2005-05-02,PRJ)
catch {package require ca}

set pvConnect__Description__ {
  Author
    Pete Jemian
  Revision Date
    2005 April 20
    2009-03-19: now, OAG Tcl Toolkit needed to locate "dp_atexit"

  Comment
    This file provides service routines for use by Tcl scripts
    (using et_wish, oagwish, or oagtclsh)
    to connect to EPICS process variables.
    They provide the EPICS variables within a Tcl global array
    named PV.  For example, 
       pvConnect S:SRcurrentAI
    will create the PV(S:SRcurrentAI) (assuming the link is successful).

    When using these routines within oagtclsh, it is necessary
    to call "update" frequently (100/sec or faster) to allow 
    Tcl to respond to EPICS Channel Access monitors.
    From et_wish or oagwish, the Tk idle event loop will manage this.
    However, within procedures which take a long time, keep
    in mind that update should be called or monitors may be missed.

  msTimeStamp
    This procedure has no arguments and returns the UNIX time stamp
    as a floating point number with a millisecond precision appended.
    This routine is called from pvMonitorRespond and others.

  pvGet pv [mode]
    This procedure gets the value of an EPICS PV.
    Its only purpose is to make sure that the value in
    the PV global array matches that of the EPICS PV.
    The optional "mode" parameter allows to use 
      w or wait         will block execution until value is received
      default           will not block execution
    Since these support routines place monitors on all PVs,
    it should not be necessary to use the "wait" mode.

  pvPut pv value [mode]
    This procedure sets (a.k.a puts) the value of an EPICS PV.
    It sets the EPICS PV to the specified value.
    The optional "mode" parameter allows to use 
      w or wait         will block execution until value is written
      q or quick        will not block execution, no notification received
      default           will not block execution, notification received

  pvMonitorRespond pv
    This procedure (called from pvConnect) will respond to an EPICS
    Channel Access monitor (set up within pvConnect) and read the
    current value of the monitored PV, setting it in the global
    array PV.  It will increment the number of times that
    monitors on this PV have been received and will write the
    time stamp (msTimeStamp) into the PV array.

  pvConnect pvList [wait]
    This procedure will link and monitor a Tcl list of EPICS PV, providing
    access to those variable through the PV global array.
    It will not link PVs already in the PV global array.
}

proc msTimeStamp {} {
  set    ms [clock clicks -milliseconds]
  set    t  [clock seconds]
  return $t.[string range $ms end-2 end]
}


proc pvTestConnect {pv} {
  global PV
  if [info exists PV($pv)] {return 1}
  if {[info exists PV(count,$pv)] && [info exists PV(time,$pv)]} {return 0}
  pvConnect $pv
  return [pvTestConnect $pv]
}

proc pvGet {pv {mode normal}} {
  global PV
  if ![pvTestConnect $pv] return
  switch -- [string tolower $mode] {
    wait -  w {set get getq}
    default   {set get get}
  }
  return [pv $get PV($pv)]
}

proc pvPut {pv value {mode normal}} {
  global PV
  if ![pvTestConnect $pv] return
  switch -- [string tolower $mode] {
    quick - q {set put putq}
    wait -  w {set put putq}
    default   {set put put}
  }
  set PV($pv) $value
  return [pv $put PV($pv)]
}

proc pvMonitorRespond {pv} {
  global PV
  if ![pvTestConnect $pv] return
  pvGet $pv
  set PV(time,$pv) [msTimeStamp]
  incr PV(count,$pv)
}

proc pvConnect {pvs {wait 1}} {
  global PV
  catch {unset tclList}
  catch {unset pvList}
  foreach pv $pvs {
    # don't link to PVs twice
    if ![info exists PV($pv)] {
      lappend tclList PV($pv)
      lappend pvList  $pv
    }
  }
  if ![info exists pvList] return
  if ![llength $pvList] return
  switch -- [string tolower $wait] {
    wait -
    1 {
      set link linkw
    }
    default {
      set link link
    }
  }
  set result [pv $link $tclList $pvList]
  foreach pv $pvList {
    set PV(count,$pv) 0
    set PV(time,$pv) [msTimeStamp]
    # umon forces widget updating
    # It should not effect adversely but may cause
    # performance penalties when monitoring many PVs
    # or for rapid updates (when many simultaneous 
    # monitors are received)
    set result [pv umon PV($pv) [list pvMonitorRespond $pv]]
    lappend PV(pvList) $pv
  }
}

#

proc pvConnect__measureTimingLoop__ args {
  set t0  [clock seconds]
  set tN  [expr $t0 + 15]
  set count 0
  for {set t $t0} {$t < $tN} {set t  [clock seconds]} {
    incr count
    if {$t != $t0} {
      puts "[msTimeStamp] [expr 1./$count]"
      set count 0
      set t0 $t
    }
    update
  }
}

proc pvConnect__simpleDemo__ args {
  global PV
  set pv S:SRcurrentAI
  #pvConnect $pv
  set tEnd [expr [clock seconds] + 20]
  pvMonitorRespond $pv
  set t0 $PV(time,$pv)
  for {} {[clock seconds] < $tEnd} {} {
    after 10
    update
    set t $PV(time,$pv)
    if {$t == $t0} continue
    puts [format "%.03f %.03f" $PV($pv) $PV(time,$pv)]
    set t0 $t
  }
}

proc pvConnect__listDemo__ args {
  global PV
  pvConnect [list S:SRcurrentAI S:IOC:timeOfDayForm1SI iad:enc:energy_corr]
  for {set i 10} {$i} {incr i -1} {
    after 1000
    update
    parray PV
    puts "#----------------"
  }
}

# run the demos if this TCL file was called directly (not included)
if {![string compare "pvConnect.tcl" [lindex [file split $argv0] end]]} {
  puts "\n\nLIST demo (displays once each second for 10 seconds)"
  pvConnect__listDemo__
  puts "\n\nSimple demo (displays continuous PV monitors for 20 seconds)"
  pvConnect__simpleDemo__
}
