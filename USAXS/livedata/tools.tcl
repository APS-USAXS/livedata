#!/usr/bin/tclsh
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
#
# tools

#####################################################################

if ![info exists tool] {
  source arrayset.tcl
}

#####################################################################

proc errorHandler { {message {}} } {
  global tool
  #puts $tool(plainContent)
  puts " A tool error ocurred. Could not process your request."
  if [string length $message] {
    puts $message
  }
  exit
}

#####################################################################

proc timeStamp args {
  return [clock format [clock seconds]]
}

#####################################################################

# replacement for caGet method
proc burtrb pvlist {
  global tool

  if ![llength $pvlist] return
  write_file $tool(burt-request) [join $pvlist \n]
  set cmd $tool(burtrb)
  append cmd " $tool(burt-switches)"
  append cmd " -f $tool(burt-request)"
  append cmd " -o $tool(burt-sdds)"
  append cmd " -l $tool(burt-log)"
  set err [catch {eval exec $cmd}]
  set buf [readSDDS $tool(burt-sdds)]
  if [llength $buf] {
    return $buf
  }
  return
}

#####################################################################

proc readSDDS file {
  if ![file exists $file] return
  set f [open $file r]
  set buf [read $f]
  close $f
  foreach line [lrange [split $buf \r\n] 1 end] {
    if ![string length $line] continue
    set c1 [string index $line 0]
    switch $c1 {
      "&" -
      "!" -
      " " -
      "\"" {}
      default {
        set pv [lindex $line 0]
	set value [lrange $line 7 end]
	set db($pv) $value
      }
    }
  }
  if [info exists db] {
    return [array get db]
  }
}

#####################################################################

proc findMotor_old text {
  global PV PV_desc findMotor_DB
  if ![info exists findMotor_DB] {
    foreach item [array names PV_desc *.RBV] {
      set pv [lindex [split $item .] 0]
      set name [string trim [lindex $PV_desc($item) 1] ,]
      set findMotor_DB($name) $pv
    }
  }
  return $findMotor_DB($text)
}

proc findMotor text {
  global  PV  XREF
  if ![info exists XREF($text)] return
  # strip away the ".RBV" part
  return [string range $XREF($text) 0 end-4]
}

#####################################################################

proc write_file {file text} {
  set f [open $file w]
  puts $f $text
  close $f
}

#####################################################################

proc report args {
  global tool  PV  XREF

  # get EPICS PV values
  switch -- $tool(PVmethod) {
    burtrb {
      # use this segment to retrieve EPICS PVs using burtrb
      set buf [burtrb $PV(pvList)]
      if ![llength $buf] return   ;# bail out if no new data available
      # we got new data from EPICS
      array set PV $buf
    }
    pvConnect {
      # use this segment to retrieve EPICS PVs using oagtclsh PV monitors
      after 500  ;# do not update any faster than 0.500 seconds
      update	 ;# this is where the PV monitors get updated, written directly into global PV array
    }
  }

  # write raw & formatted data tables to WWW text files
  catch {writeRawFile}
  catch {writeStatusFile}

  # actually update the WWW page?
  if ![info exists tool(white_shtr_closed,lastvalue)] {
    set tool(white_shtr_closed,lastvalue) not-set-yet
  }
  switch -- [string tolower $PV($XREF(white_shtr_closed))] {
    open {createHTML}
    closed___ {
      ### 2007-03-14,PRJ:
      ### always update WWW page content
      # if white shutter remains closed,
      # no need to update WWW page content
      set lastState [string tolower $tool(white_shtr_closed,lastvalue)]
      if ![string compare $lastState open ] {
        # white shutter closed since last pass through this code.
        catch {createHTML}
      }
    }
    default {createHTML}
  }
  # remember the white shutter setting, use it next time around
  set tool(white_shtr_closed,lastvalue) $PV($XREF(white_shtr_closed))

  # update SPEC macro file on WWW directory if new
  catch {
    set wwwFile [file join $tool(baseNFS) $tool(specmacro)]
    set tmpFile [file join /tmp 	  $tool(specmacro)]
    set www [file mtime $wwwFile]
    set tmp [file mtime $tmpFile]
    if {$tmp > $www} {
      file copy -force $tmpFile $wwwFile
    }
  }
}

#####################################################################

proc writeRawFile args {
  global tool  PV  XREF
  set fmt "%s\t%s"
  set dataFileName [file join $tool(baseNFS) $tool(rawFile)]
  set timeStamp [timeStamp]
  lappend lines [format $fmt file	 $dataFileName]
  lappend lines [format $fmt description $tool(title)]
  lappend lines [format $fmt timeStamp   $timeStamp]
  lappend lines [format $fmt epoch	   [clock scan $timeStamp]]
  foreach item [lsort [array names PV]] {
    lappend lines [format $fmt $item $PV($item)]
  }
  write_file $dataFileName [join $lines \n]
}

#####################################################################

proc writeStatusFile args {
  global tool  PV  XREF  Description
  array set fieldWidth {
    desc  0
    value 0
    pv    0
  }
  set fileName [file join $tool(baseNFS) $tool(statusFile)]
  foreach var [lsort [array names Description]] {
    set desc $Description($var)
    set pv   $XREF($var)
    set fieldWidth(desc)  [chooseMax $fieldWidth(desc)  [string length $desc]]
    set fieldWidth(value) [chooseMax $fieldWidth(value) [string length $PV($pv)]]
    set fieldWidth(pv)    [chooseMax $fieldWidth(pv)	[string length $pv]]
  }
  set    fmt ""
  append fmt "%-[set fieldWidth(desc)]s"
  append fmt "\t"
  append fmt "%-[set fieldWidth(pv)]s"
  append fmt "\t"
  append fmt "%-[set fieldWidth(value)]s"
  lappend output "# file: $fileName"
  lappend output "# description: $tool(title)"
  lappend output "# timeStamp: [timeStamp]"
  lappend output "#####################################################"
  foreach var [array names XREF] {
    # these lines are out of order
    set pv   $XREF($var)
    set desc $var
    catch {set desc $Description($var)}
    set lines($desc) [format $fmt $desc $pv $PV($pv)]
  }
  foreach desc [lsort -dictionary [array names lines]] {
    # sort them by their descriptions
    lappend output $lines($desc)
  }
  write_file $fileName [join $output \n]
}

#####################################################################

proc chooseMax {a b} {
  set max $a
  if {$b > $a} {set max $b}
  return $max
}

#####################################################################

proc makePlot {} {
  global tool  PV  XREF

  set now [clock seconds]
  if ![info exists tool(makePlot_time)] {
    set tool(makePlot_time) 0
  }
  # don't update the plot too frequently
  if {$now < $tool(makePlot_time)} return

  set numScans 5
  set pltFile $tool(baseNFS)/$tool(pltFile)
  set specFile [file join $PV($XREF(spec_dir)) $PV($XREF(spec_data_file))]
  # make sure that the file exists
  if ![file exists $specFile] return
  # and it _is_ a file
  if ![file isfile $specFile] return

  set cksum [lindex [eval exec cksum $specFile] 0]
  if [info exists tool(makePlot_specFileChecksum)] {
    # don't update the plot if there is no new data
    if {$cksum == $tool(makePlot_specFileChecksum)} return
  }

  usaxs_plot $specFile $numScans $pltFile $tool(plotFormat)
  set tool(makePlot_time) [expr $now + $tool(replotInterval_s)]
  set tool(makePlot_specFileChecksum) $cksum
}

#####################################################################

# start the reporting
proc mainLoop args {
  global  tool  PV  XREF
  if [catch {report} errorMessage] {
    puts "[timeStamp]:  Error from <report> procedure:\n$errorMessage\n"
  }
  if [catch {makePlot} errorMessage] {
    set    message [clock format [clock seconds]]
    append message ": makePlot returned an error"
    append message ":\n$errorMessage"
    if [info exists   PV($XREF(spec_dir))] {
      if [info exists PV($XREF(spec_data_file))] {
        set file [file join $PV($XREF(spec_dir)) $PV($XREF(spec_data_file))]
        append message ":\nspecdata file: $file"
      }
    }
    append message ": tcl error stack"
    catch {append message ":\n$errorInfo"}
    puts $message\n
  }
  after $tool(waitInterval_ms)
}
