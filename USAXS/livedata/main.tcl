#! /bin/sh
#
# the next line restarts using OAG Tcl shell oagtclsh \
   exec oagtclsh "$0" ${1+"$@"}

# update a file with new EPICS data for 32ID-B USAXS experiment

#####################################################################

set tool(homedir) /home/joule/USAXS/code/livedata/
lappend auto_path $tool(homedir)
set pvList [readConfig]

switch -- $tool(PVmethod) {
  burtrb {
    set PV(pvList) $pvList
  }
  pvConnect {
    unset PV
    pvConnect $pvList
    update
  }
}

#####################################################################

puts "[clock format [clock seconds]]: $argv0 starting (PID=[pid])\n"

while {1} { mainLoop }
#mainLoop

set HELPFUL_DIAGNOSTIC {
  set f [open burt.req w]
  puts $f [join [lsort $PV(pvList)] \n]
  close $f
}
