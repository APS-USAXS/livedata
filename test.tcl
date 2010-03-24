#! /bin/sh
#
# the next line restarts using OAG Tcl shell oagtclsh \
   exec oagtclsh "$0" ${1+"$@"}

# update a file with new EPICS data for 32ID-B USAXS experiment

#####################################################################

set tool(homedir) /home/joule/USAXS/code/livedata/
lappend auto_path $tool(homedir)
set pvList [readConfig]

#####################################################################

puts "[clock format [clock seconds]]: $argv0 starting (PID=[pid])\n"

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

foreach item {1 2 3 4 5 6 7 8 9 10} {
  after 500
  update
  parray PV *S:SR*
  puts "#--------------------"
}
