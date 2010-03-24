#!/usr/bin/tclsh
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
#
# file: usaxs_plot.tcl
# create a plot from current USAXS experiments to a PNG file
# harvest the USAXS data from the named SPEC data file

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

#puts "found the spec file"

  set cksum [lindex [eval exec cksum $specFile] 0]
  if [info exists tool(makePlot_specFileChecksum)] {
    # don't update the plot if there is no new data
    if {$cksum == $tool(makePlot_specFileChecksum)} return
  }

#puts "spec file has new data"

  usaxs_plot $specFile $numScans $pltFile $tool(plotFormat)
  set tool(makePlot_time) [expr $now + $tool(replotInterval_s)]
  set tool(makePlot_specFileChecksum) $cksum
}

#####################################################################

proc usaxs_plot args {
  global specData tool
  if {[llength $args] != 4} {
    error "usage: usaxs_plot specFile numScans pltFile plotFormat"
    return
  }
  set specFile   [lindex $args 0]
  set numScans   [lindex $args 1]
  set pltFile    [lindex $args 2]
  set plotFormat [lindex $args 3]
  # # # # #
  if ![file exists $specFile] return
  if {$numScans} {
    set numScans [expr abs($numScans)]
  } else {
    set numScans 5
  }
  # # # # #
  #
  # parse the spec file for USAXS scans
  catch {unset specData}
  readSpecFile $specFile
#puts "read the spec file"
  # find the USAXS scans
  if ![info exists specData(scanList)] return
  catch {unset usaxsScanListAll}
  foreach item $specData(scanList) {
    switch -- [lindex $specData($item,line1) 2] {
      sbuascan -
      uascan {
        lappend usaxsScanListAll $item
	#puts $item
      }
    }
  }
  if ![info exists usaxsScanListAll] return
#puts "spec file has usaxs scan(s)"
  # return a list of the n-most recent USAXS scans, oldest first
  set usaxsScanNumList [lrange $usaxsScanListAll end-[expr $numScans-1] end]
  # extract the USAXS from each of those scans, in order
  foreach scanNum $usaxsScanNumList {
    set result [calc_usaxs_data $scanNum]
    set usaxs_data($scanNum,title) [lindex $result 0]
    set usaxs_data($scanNum)	   [lindex $result 1]
  }
#puts "spec file usaxs scan(s): $usaxsScanNumList"

  # prepare this data for use by ploticus
  set format "%-10s %s %s"
  foreach scanNum $usaxsScanNumList {
    foreach datum $usaxs_data($scanNum) {
      set USAXS_Q [expr abs([lindex $datum 0])]
      set USAXS_I [lindex $datum 1]
      set label S$scanNum
      if {($USAXS_Q == 0.0) || ($USAXS_I <= 0)} {
        set label ignore 
      } else {
        if ![info exists Qmin] {
	  set Qmin $USAXS_Q
	} else {
	  if {$USAXS_Q < $Qmin} {set Qmin $USAXS_Q}
	}
        if ![info exists Qmax] {
	  set Qmax $USAXS_Q
	} else {
	  if {$USAXS_Q > $Qmax} {set Qmax $USAXS_Q}
	}
        # strange ploticus bug that will not plot any data when Qmax/Qmin < 2.9
        if {$Qmax < 3*$Qmin} {
	  set Qmax [expr 3*$Qmin]
	}
        if ![info exists Imin] {
	  set Imin $USAXS_I
	} else {
	  if {$USAXS_I < $Imin} {set Imin $USAXS_I}
	}
        if ![info exists Imax] {
	  set Imax $USAXS_I
	} else {
	  if {$USAXS_I > $Imax} {set Imax $USAXS_I}
	}
      }
      lappend output [format $format $label $USAXS_Q $USAXS_I]
    }
  }
  if ![info exists output] return
#puts "spec file usaxs scan(s) extracted"
  # write this data to a temporary file
  set root /tmp/[pid]-[format %08x [clock seconds]]
  set tempDataFile $root.dat
  set tempPloticusFile $root.pl
  set tempPltFile $root.$plotFormat
  set f [open $tempDataFile w]
  puts $f "dataset	Qvec		Intensity"
  puts $f [join $output \n]
  close $f
  #
  # prepare the ploticus command file
  set ploticus(specFile) $specFile
  set ploticus(dataFile) $tempDataFile
  set ploticus(title)    $specFile
  set ploticus(Qmin)     1e-5
  set ploticus(Qmax)     1.0
  set ploticus(Qmin)     $Qmin
  set ploticus(Qmax)     $Qmax
  set ploticus(Imin)     $Imin
  set ploticus(Imax)     $Imax
  set ploticus(scanList) S[join $usaxsScanNumList " S"]
  foreach scanNum $usaxsScanNumList {
    set ploticus(S$scanNum,title) "#$scanNum: $usaxs_data($scanNum,title)"
  }
  set ploticus(script) [create_ploticus_script [array get ploticus]]
  set f [open $tempPloticusFile w]
  puts $f $ploticus(script)
  close $f
#puts "ploticus prepared"
  #
  # execute the ploticus script
  catch {
    set    cmd $tool(ploticus)
    #set cmd /usr/bin/pl
    append cmd " $tempPloticusFile -$plotFormat -o $tempPltFile"
#puts "ploticus command: $cmd"
    catch {eval exec $cmd}
#puts "ploticus executed"
    catch {file attributes $pltFile -permissions +rw}
    file copy -force $tempPltFile   $pltFile
    catch {file attributes $pltFile -permissions +rw}
#puts "files copied"
    #
    # clean-up
    file copy -force $tempDataFile     /tmp/usaxs_livedata_data.dat
    file copy -force $tempPloticusFile /tmp/usaxs_livedata_plot.pl
    file copy -force $tempPltFile      /tmp/usaxs_livedata_plot.$plotFormat
#puts "files copied to WWW site"
    catch {file delete -force $tempDataFile}
    catch {file delete -force $tempPloticusFile}
    catch {file delete -force $tempPltFile}
#puts "temporary files deleted"
  }
}

#####################################################################

proc calc_usaxs_data scanNum {
  global  specData

  set pi   [expr 4*atan(1.0)]
  set d2r  [expr $pi/180]

  interpretScanID $scanNum

	    # assume first comment has sample title
  set item "$scanNum,#C"
  if ![info exists specData($item)] return
  set item [lindex [split $specData($item) \r\n] 0]
  set sampleTitle [string trim [string range $item 2 end]]

# ??? something missing here ???

  set item "$scanNum,value,ARenc_0"
  if [info exists specData($item)] {
    # this variable was added 2003-01-31 to the spec file header
    set ar_enc0  $specData($item)
  } else {
    ## (assume AR is set to AR0 at start of scan)
    ##puts [lsort [array names specData $scanNum,value,*]]
    if ![info exists specData($scanNum,value,arEnc)] return
    # screwy on 2003-11-18, PRJ placed this wretched hack here
    set ar_enc0  $specData($scanNum,value,arEnc)
  }
  set lambda   $specData($scanNum,value,DCM_lambda)
  if ![info exists specData($scanNum,ar_enc)] return
  set numData [llength $specData($scanNum,ar_enc)]
  catch {unset output}
  if [catch {
    for {set row 0} {$row < $numData} {incr row} {
      set ar_enc       [lindex $specData($scanNum,ar_enc)    $row]
      set diode_range  [lindex $specData($scanNum,pd_range)  $row]
      set count_time   [lindex $specData($scanNum,seconds)   $row]
      set diode_cts    [lindex $specData($scanNum,pd_counts) $row]
      set mon_cts      [lindex $specData($scanNum,I0)	     $row]
      set USAXS_Q [expr (4*$pi/$lambda)*sin($d2r*($ar_enc0 - $ar_enc)/2)]
      scan $specData($scanNum,value,UPD2gain$diode_range) %g diode_gain
      set dark_curr    $specData($scanNum,value,UPD2bkg$diode_range)
      set V_f_gain 1e5
      set USAXS_I [expr ($diode_cts - $count_time*$dark_curr)/$diode_gain / $mon_cts / $V_f_gain]
      lappend output   [list $USAXS_Q $USAXS_I]
    }
  }] return
  if ![string length $output] {
    puts "[clock format [clock seconds]]: error in calc_usaxs_data"
    puts "sample <$sampleTitle> has no data!"
  }
  return [list $sampleTitle $output]
}

#####################################################################

proc create_ploticus_script args {
  #puts $args
  array set ar [lindex $args 0]
  set    output "#proc page\n"
  append output "  backgroundcolor: rgb(1.0,0.94,0.85)\n"
  append output "\n"

  append output "#proc annotate\n"
  append output "  location:  1 0.45\n"
  append output "  textdetails: align=L size=6\n"
  append output "  text: APS XOR/32 32ID-B USAXS data\n"
  append output "\n"

  append output "#proc annotate\n"
  append output "  location:  1 0.35\n"
  append output "  fromcommand: date\n"
  append output "  textdetails: align=L size=6\n"
  append output "\n"

  append output "#proc getdata\n"
  append output "  fieldnameheader: yes\n"
  append output "  delim: whitespace\n"
  append output "  commentchar: #\n"
  append output "  file:  $ar(dataFile)\n"
  append output "\n"

  append output "#proc areadef \n"
  append output "  rectangle: 1 1 7 7\n"
  append output "  areacolor: rgb(0.95,1.0,0.97)\n"
  append output "  frame: color=rgb(0.2,0.2,0.1) width=3.0\n"
  append output "  title: $ar(title)\n"
  append output "  titledetails: align=C size=24\n"
  append output "  xscaletype: log\n"
  append output "  xrange: [format "%.20f %.20f" $ar(Qmin) $ar(Qmax)]\n"
  append output "  yscaletype: log\n"
  append output "  yrange: [format "%.30f %.30f" $ar(Imin) $ar(Imax)]\n"
  #append output "  yautorange: datafield=3\n"
  append output "\n"

  append output "#proc xaxis \n"
  append output "  label: |Q|, 1/A \n"
  append output "  labeldetails: size=18\n"
  append output "  selflocatingstubs: text\n"
  set start  [expr int(floor(log10($ar(Qmin))))]
  set finish [expr int(ceil( log10($ar(Qmax))))]
  for {set y $start} {$y <= $finish} {incr y} {
    append output "  1e$y  1e$y\n"
    for {set x 2} {$x <= 9} {incr x} {
      append output "  [set x]e[set y]\n"
    }
  }
  append output "  #include \$chunk_logtics\n"
  append output "  stubrange:  $ar(Qmin) $ar(Qmax)\n"
  append output "  grid: yes \n"
  append output "  grid color=grey(0.8)\n"
  append output "\n"

  append output "#proc yaxis \n"
  append output "  label: USAXS intensity, a.u. \n"
  append output "  labeldetails: size=18\n"
  append output "  selflocatingstubs: text\n"
  set start  [expr int(floor(log10($ar(Imin))))]
  set finish [expr int(ceil( log10($ar(Imax))))]
  for {set y $start} {$y <= $finish} {incr y} {
    append output "  1e$y  1e$y\n"
    for {set x 2} {$x <= 9} {incr x} {
      append output "  [set x]e[set y]\n"
    }
  }
  append output "  #include \$chunk_logtics\n"
  append output "  stubrange: $ar(Imin) $ar(Imax)\n"
  append output "  grid: yes\n"
  append output "  grid color=grey(0.8)\n"
  append output "\n"

  # older curves are from a color sequence
  set symbolList "triangle diamond square downtriangle lefttriangle righttriangle"
#  set colorlist  " black blue purple green "
  set colorlist  " green purple blue black "
  set i 0
  foreach scan [lrange $ar(scanList) 0 end-1] {
    set color [lindex $colorlist [expr $i % [llength $colorlist]]]
    #puts "$i $color ($colorlist) [llength $colorlist] [expr $i % [llength $colorlist]]"
    append output "#proc lineplot \n"
    append output "  xfield: 2\n"
    append output "  yfield: 3\n"
    append output "  linedetails: color=$color width=0.5\n"
    set thisSymbol [lindex $symbolList [expr $i % [llength $symbolList]]]
    append output "  pointsymbol: shape=$thisSymbol radius=0.025 linecolor=$color fillcolor=white\n"
    append output "  legendlabel: $ar($scan,title)\n"
    append output "  select: @@dataset == $scan\n"
    append output "\n"
    incr i
  }

  # most recent curve is RED
  set scan [lindex $ar(scanList) end]
  append output "#proc lineplot \n"
  append output "  xfield: 2\n"
  append output "  yfield: 3\n"
  append output "  linedetails: color=red width=0.5\n"
  append output "  pointsymbol: shape=nicecircle radius=0.025 linecolor=red fillcolor=white\n"
  append output "  legendlabel: $ar($scan,title)\n"
  append output "  select: @@dataset == $scan\n"
  append output "\n"

  append output "#proc rect\n"
  append output "  rectangle: 4.2 5.7   6.8 6.8\n"
  append output "  color: white\n"
  append output "  bevelsize: 0.05\n"
  append output "\n"

  append output "#proc legend\n"
  append output "  location: 4.5 6.7\n"
  append output "  seglen: 0.2\n"
  append output "  format: multiline\n"
  append output "  textdetails: align=R\n"

  return $output
}

#####################################################################

proc interpretSpecFileHeader args {
  global tool specData

  set scanID fileHeader
  # make certain that we have a file header
  if ![info exists specData($scanID)] return

  # we've already interpreted the file header, bail out now
  if [info exists specData($scanID,interpreted)] return

  setStatus "interpreting file header"
  set part $specData($scanID)
  foreach line [split $part \r\n] {
    if {![string compare [string index $line 0] "#"]} {
      # next line was:   string index $part 1
      switch -- [string index $line 1] {
  	C	{
  	  # puts <$line>
  	  append specData($scanID,#C) $line\n
  	}
  	default {
  	  set specData($scanID,[lindex $line 0]) $line
  	}
      }
    }
  }
  # get the labels of items logged in the scan headers
  array set typeName {
    O motor
    H value
  }
  foreach type [array names typeName] {
    catch {unset specData($scanID,list,$typeName($type))}
    foreach line [array names specData $scanID,#$type*] {
      set row [string range [lindex [split $line ,] end] 2 end]
      set col 0
      # this next will break if motor names have an embedded space!
      foreach item [lrange $specData($line) 1 end] {
    	incr col
    	set specData($scanID,$typeName($type),$item) [list $row $col]
	lappend specData($scanID,list,$typeName($type)) $item
      }
    }
  }
  set specData($scanID,interpreted) 1
}


#####################################################################

proc interpretScanID scanID {
  global tool specData

  # make certain that we have this scan first
  if ![info exists specData($scanID)] return

  # we've already interpreted this scan, bail out now
  if [info exists specData($scanID,header)] return

  # ensure the file header has been interpreted
  interpretSpecFileHeader
  #
  setStatus "interpreting scan $scanID"
  set part $specData($scanID)
  catch {unset scanHeader}
  catch {unset scanData}
  foreach full_line [split $part \r\n] {
    set line [string trim $full_line]
    if ![string length $line] continue
    if {[string compare [string index $line 0] "#"]} {
      lappend scanData $line
    } else {
      lappend scanHeader $line
      # next line was:   string index $part 1
      switch -- [string index $line 1] {
  	C	{
  	  # puts <$line>
  	  append specData($scanID,#C) $line\n
  	}
  	default {
  	  set specData($scanID,[lindex $line 0]) $line
  	}
      }
    }
  }
  set specData($scanID,header) [join $scanHeader \n]
  set specData($scanID,line1)  [lindex [split $part \n] 0]
  # get the column labels
  set searchText  "  +"
  set replaceText \t

  # if no labels, then no data
  if ![info exists specData($scanID,#L)] {
    setStatus "no labels in $scanID"
    return
  }

  set labelText [string range $specData($scanID,#L) 3 end]
  regsub -all $searchText $labelText $replaceText labels
  set specData($scanID,labels) [split $labels \t]
  set numLabels [llength $specData($scanID,labels)]
  # build a list for each data column
  # index by column label and scanID
  if {[info exists scanData]} {
    foreach line $scanData {
      for {set i 0} {$i < $numLabels} {incr i} {
  	set thisLabel [lindex $specData($scanID,labels) $i]
  	set thisValue [lindex $line $i]
  	lappend specData($scanID,$thisLabel) $thisValue
      }
    }
  } else {
    #puts "no data for $scanID"
  }
  # get the labels of items logged in the scan headers
  array set typeName {
    P motor
    V value
  }
  foreach type [array names typeName] {
    foreach item $specData(fileHeader,list,$typeName($type)) {
      set row [lindex $specData(fileHeader,$typeName($type),$item) 0]
      set col [lindex $specData(fileHeader,$typeName($type),$item) 1]
      set value [lindex $specData($scanID,#$type$row) $col]
      set specData($scanID,$typeName($type),$item) $value
    }
  }
}
