#!/usr/bin/tclsh
#
# wwwpage.tcl

#####################################################################

proc htmlMotorValueInTable pv {
  global PV
  array set colorTable {
    0 #22ff22
    1 white
  }
  set	 value $PV($pv.RBV)
  set	 dmov  $PV($pv.DMOV)
  set options(indent) 0
  set options(tagOptions) [format {BGCOLOR="%s"} $colorTable($dmov)]
  return [htmlTag TD [format %.6f $value] 0 $options(tagOptions)]
}

#####################################################################

proc createHTML_head {title} {
  global tool
  set    head	{<meta HTTP-EQUIV="Pragma" CONTENT="no-cache">}
  append head	\n
  append head	[format {<meta HTTP-EQUIV="Refresh" CONTENT=%s>} $tool(htmlRefresh_s)]
  append head	\n[htmlTag TITLE $tool(title)]
  set css {
    BODY { font: x-small Verdana, Arial, Helvetica, sans-serif; }
    h1 {font-size: 145%; margin-bottom: .5em; }
    h2 {
    	    font-size: 125%;
    	    margin-top: 1.5em;
    	    margin-bottom: .5em; }
    h3 {
    	    font-size: 115%;
    	    margin-top: 1.2em;
    	    margin-bottom: .5em}
    h4 {
    	    font-size: 100%;
    	    margin-top: 1.2em;
    	    margin-bottom: .5em; }
    P {
    	    font: x-small Verdana, Arial, Helvetica, sans-serif;
    	    color: #000000; }
    .description {  font-weight: bold; font-size: 150%;}
    TD {    font-size: x-small; }

    LI {
    	    margin-top: .75em;
    	    margin-bottom: .75em; }
    UL {    list-style: disc; }

    UL UL, OL OL, OL UL, UL OL {
    	    margin-top: 1em;
    	    margin-bottom: 1em; }
    LI P {
    	    margin-top: .5em;
    	    margin-bottom: .5em; }

    .dt {
    	    margin-bottom: -1em; }
    .indent {
    	    margin-left: 1.5em; }
    SUP {
    	    text-decoration: none;
    	    font-size: smaller; }
  }
  append head	\n[htmlTag STYLE $css 1 {TYPE="text/css"}]
  return	[htmlTag HEAD $head]
}


#####################################################################

proc normalizeShutterState {value} {
  switch -- [string tolower $value] {
    0 -
    off -
    closed {
      set state closed
    }
    1 -
    on -
    open {
      set state open
    }
    default {
      set state $value
    }
  }
  return $state
}

#####################################################################

proc createHTML args {
  global tool  PV  XREF
  #
  set grey #dddddd
  set emptyCell  [htmlTag TD $tool(nbsp) 0 BGCOLOR=$grey]
  array set colors {
    on	     #22ff22
    off      #ff2222
    open     #22ff22
    closed   #ff2222
    {}	     lightgrey
  }
  set table_tags "border=1 width=100% BGCOLOR=mintcream rules=all"
  #
  #
  #-----------------------------------------------------------------
  #
  # HEAD
  #
  set html(head)   [createHTML_head $tool(title)]
  #
  # BODY
  #
  set    body ""
  set period [format %g [expr $tool(waitInterval_ms)*0.001]]
  set htmlRefreshMesg  [format "HTML page refresh interval %d:%02d:%02d (h:mm:ss)" \
  		   [expr $tool(htmlRefresh_s) / 3600] \
  		   [expr ($tool(htmlRefresh_s) % 3600 / 60)] \
  		   [expr $tool(htmlRefresh_s) % 60] \
		 ]
    #
    set rows ""
    set text $tool(title)
    append rows   [htmlTag TR \
    	  [htmlTag TD \
    		  [htmlTag FONT $text 0 \
    			  {COLOR=white}] 0 {align="center" CLASS="description"}]]
    append rows \n[htmlTag TR \
    	  [htmlTag TD \
    		  [htmlTag FONT $htmlRefreshMesg 0 \
    			  {COLOR=white}] 0 {align="center"}]]
    set url $tool(webcam)
      set    href  HREF="$url"
      set    label [htmlTag A $url 0 HREF="$url"]
      set    row   [htmlTag TD "Webcam: $label" 1 {align="center"}]
    append rows \n[htmlTag TR $row 1 {BGCOLOR="lightblue"}]


    # write a row with the raw data
      set    url   $tool(rawDataURL)
      set    href  HREF="$url"
      set    label [htmlTag A "raw" 0 HREF="$tool(rawDataURL)"]
      append label "\n / "
      append label \n[htmlTag A "descriptive" 0 HREF="$tool(statusFile)"]
      append label "\n / "
      append label \n[htmlTag A "scan log" 0 HREF="$tool(scanLogURL)"]
      append label "\ncontent updated:"
      append label \n[timeStamp]
      set    emph  [htmlTag EM $label 1]
      set    font  [htmlTag FONT $emph 1]
    append rows  \n[htmlTag TR [htmlTag TD $font 1 {align="center"}] 1 {BGCOLOR="lightblue"}]

    set rowAttributes {border=0 width=96% rules=none BGCOLOR=darkblue}
  append body \n[htmlTag TABLE $rows 1 $rowAttributes]
  #
  # subtable: shutter states
  set	 row  [htmlTag TD shutters:]
    set label "USAXS CCD"
    set state [normalizeShutterState $PV($XREF(CCD_shtr_closed))]
  append row   [htmlTag TD "$label: $state" 0 BGCOLOR=$colors([string tolower $state])]
    set label "USAXS Ti filter"
    set state [normalizeShutterState $PV($XREF(Ti_shtr_open))]
  append row \n[htmlTag TD "$label: $state" 0 BGCOLOR=$colors([string tolower $state])]
    set label "mono"
    set state $PV($XREF(mono_shtr_closed))
  append row \n[htmlTag TD "$label: $state" 0 BGCOLOR=$colors([string tolower $state])]
    set label "white"
    set state $PV($XREF(white_shtr_closed))
    set subtext "$label: $state"
    if {$PV($XREF(white_shtr_auto))} {
      append subtext " (auto)"
    }
  append row \n[htmlTag TD $subtext 0 BGCOLOR=$colors([string tolower $state])]
    set    table    [htmlTag TABLE [htmlTag TR $row 1] 1 {border=1 width=100% rules=all}]
  set rows [htmlTag TR [htmlTag TD $table 1] 1]
  #
  # subtable: APS, ID, DCM

  set url  $tool(APSstatusPlot)
  set href HREF="$url"
  set label [htmlTag A "APS current" 1 $href]\n
  if {$PV($XREF(SR_current)) > 1} {
    set ringCurrentGood   on
  } else {
    set ringCurrentGood   off
  }
    set row   [htmlTag TD \
                 "$label = [format %.2f $PV($XREF(SR_current))] mA" \
		 0 BGCOLOR=$colors($ringCurrentGood)]
    append row \n[htmlTag TD [format "ID E = %.3f keV" $PV($XREF(Und_E))]]
    append row \n[htmlTag TD [format "DCM E = %.3f keV" $PV($XREF(DCM_E))]]
    set    table     [htmlTag TABLE [htmlTag TR $row 1] 1 $table_tags]
    append rows \n[htmlTag TR [htmlTag TD $table 1] 1]
  #
  # subtable: Q and Intensity
  set    row	   [htmlTag TD "|Q| = $PV($XREF(USAXS_Q)) 1/A" ]
    #
    # recalculate the intensity since 32idbLAX:USAXS:I is often an underflow value
    # use pA/uA
    set gain $PV($XREF(I0_amp_gain))
    set I0_current   [expr -1.0*$PV($XREF(I0_VDC)) / $gain ]
    set gain $PV($XREF(diode_amp_gain))
    set upd2_current [expr  1.0*$PV($XREF(diode_VDC)) / $gain ]
    if {$I0_current > 0} {
      set intensity [format %e [expr 1e6 * $upd2_current / $I0_current]]
    } else {
      set intensity 0
    }
    append row	 \n[htmlTag TD "I = $intensity pA/uA"]
    append row	 \n[htmlTag TD [format "SAD = %f mm" $PV($XREF(SAD))]]
    append row	 \n[htmlTag TD [format "SDD = %f mm" $PV($XREF(SDD))]]
    set    table     [htmlTag TABLE [htmlTag TR $row 1] 1 $table_tags]
    append rows \n[htmlTag TR [htmlTag TD $table 1] 1]
  #
  # subtable: mirror position
  set mirrorPos {none}
  if {$PV($XREF(mirror_rh_pos))}    {set mirrorPos {Rh stripe}}
  if {$PV($XREF(mirror_cr_pos))}    {set mirrorPos {Cr stripe}}
  if {$PV($XREF(mirror_si_pos))}    {set mirrorPos {Si stripe}}
  if {$PV($XREF(mirror_wh_pos))}    {set mirrorPos {white beam pass-by}}
  #
  set    text "mirror position: $mirrorPos"
  set    subRows   [htmlTag TD $text 1]
  #
  # subtable: PF4 filter/attenuator box
  set    text "PF4 filter transmission: "
  append text [format %.2g $PV($XREF(pf4_trans))]
  append text " ("
  append text "Al=[format %g $PV($XREF(pf4_thickness_Al))] mm"
  append text ", "
  append text "Ti=[format %g $PV($XREF(pf4_thickness_Ti))] mm"
  append text ", "
  append text "glass=[format %g $PV($XREF(pf4_thickness_Gl))] mm"
  append text ")"
  append    subRows   \n[htmlTag TD $text 0]
  #
  set    table     [htmlTag TABLE [string trim $subRows] 1 $table_tags]
  append rows \n[htmlTag TR [htmlTag TD $table 1] 1]
  # sample title and scan status
  append rows    [htmlTag TR \
  	[htmlTag TD \
		[cleanString $PV($XREF(sampleTitle))] 0 \
			{align="center" BGCOLOR=bisque CLASS="description"}]]
  append rows \n[makeTagHTML TR \
    [makeTagHTML \
      {TD align="center" BGCOLOR=lightblue} \
      [makeTagHTML {FONT SIZE=4} [cleanString $PV($XREF(state))] 0]\
      0\
    ]\
  ]
  # subtable: macro file and start time
  set url  $tool(specmacro)
  set href HREF="$url"
  set label [makeTagHTML "A $href" $PV($XREF(spec_macro_file)) 0]\n
  set    subRows   [makeTagHTML {TD align="left"} "spec macro: [string trim $label]" 0]
  set    stamp [clock format [file mtime $tool(baseNFS)/$tool(specmacro)]]
  set    label "time stamp: $stamp"
  append subRows \n[makeTagHTML {TD align="center"} $label 0]
  switch -- $PV($XREF(USAXS_collecting)) {
    ON {
      append subRows \n[makeTagHTML {TD align="center" BGCOLOR=lightgreen} "USAXS scan in progress" 0]
    }
    OFF {
      append subRows \n[makeTagHTML {TD align="center"} "not scanning USAXS" 0]
    }
  }
  set    table     [makeTagHTML "TABLE $table_tags" [string trim $subRows]]
  append rows \n[makeTagHTML TR [makeTagHTML TD $table]]
  # subtable: specfile and scan
  set    subRows   [htmlTag TD \
  	$PV($XREF(spec_dir))/$PV($XREF(spec_data_file)) 0 \
		{align="left"}]
  append subRows \n[makeTagHTML {TD align="center"} "scan #[cleanString $PV($XREF(spec_scan))]" 0]
  append subRows \n[makeTagHTML {TD align="center"} [cleanString $PV($XREF(timeStamp))] 0]
  set    table     [makeTagHTML "TABLE $table_tags" [string trim $subRows]]
  append rows    \n[makeTagHTML TR [makeTagHTML TD $table]]
  #
  # table: build heading table
  append body \n[makeTagHTML {TABLE border=1 width=96% rules=all} $rows]
  #
  set motorTable {
    stage	rot,deg	encoder,deg	X,mm	Y,mm	Z,mm	tilt,deg
    m		mr 	enc,MR          mx	my	-	-
    ms  	msr	-	        msx	msy	-	mst
    s		-  	-	        sx	sy	-	-
    as  	asr	-	        asx	asy	-	ast
    a		ar 	enc,AR          ax	ay	az	-
    d		-  	-	        dx	dy	-	-
    "DCM theta"  DCM_theta  -		-	-	-	-
    mirror	- 	-		mirr_x	mirr_vs	-	-
    tcam	tcam 	-		-	-	-	-
  }
  catch {unset rows}
  set labelRow 1
  foreach line [split [string trim $motorTable] \r\n] {
    set row [makeTagHTML TD [lindex $line 0]]
    foreach item [lrange $line 1 end] {
      if {$labelRow} {
        append row \n[makeTagHTML TD $item 0]
      } else {
        if [string compare $item "-"] {
	  if [string compare [string range $item 0 2] "enc"] {
	    append row \n[htmlMotorValueInTable [findMotor $item]]
	  } else {
	    switch -- [lindex [split [string tolower $item] ,] end] {
	      mr {set value $PV($XREF(mr_enc))}
	      ar {set value $PV($XREF(ar_enc))}
	      default {set value ?}
	    }
	    append row \n[makeTagHTML TD [format %.6f $value] 0]
	  }
	} else {
	  append row \n$emptyCell
	}
      }
    }
    append rows  \n[makeTagHTML TR $row]
    set labelRow 0
  }
  set table        [makeTagHTML {TABLE BORDER=2} [string trim $rows]]
  set    html(motorBlock)   [makeTagHTML H4 motors]$table
  #append body \n[htmlTag BR]
  #append body \n$html(motorBlock)
  #
  catch {unset rows}
  #------------ detector column labels ----------------
  set    row	   [makeTagHTML TD detector  0]
    append row	 \n[makeTagHTML TD counts    0]
    append row	 \n[makeTagHTML TD VDC       0]
    append row	 \n[makeTagHTML TD gain,V/A  0]
    append row	 \n[makeTagHTML TD current,A 0]
    append rows  \n[makeTagHTML TR $row]
  #------------ I0 ----------------
  set    row	   [makeTagHTML TD I0       ]
    switch -- $PV($XREF(scaler_cnt)) {
      Done    {set bkg BGCOLOR="white"}
      default {set bkg BGCOLOR="#00ff00"}
    }
    append row	 \n[htmlTag TD $PV($XREF(scaler_I0)) 0 $bkg]
    append row	 \n[htmlTag TD [format %.4f $PV($XREF(I0_VDC))]]
    append row	 \n[htmlTag TD [format %.1e $PV($XREF(I0_amp_gain))]]
    set current  $I0_current
    #set current 0
    append row	 \n[htmlTag TD [format %e $current]]
    append rows  \n[htmlTag TR $row 1]
  #------------ I00 ----------------
  set    row	   [htmlTag TD I00]
    append row	 \n[htmlTag TD $PV($XREF(scaler_I00)) 0 $bkg]
    append row	 \n[htmlTag TD [format %.4f $PV($XREF(I00_VDC))]]
    append row	 \n[htmlTag TD [format %.1e $PV($XREF(I00_amp_gain))]]
    if {$PV($XREF(I00_amp_gain)) > 0} {
      set current [expr -1.0*$PV($XREF(I00_VDC)) / $PV($XREF(I00_amp_gain))]
    } else {
      set current 0
    }
    append row	 \n[htmlTag TD [format %e $current]]
    append rows  \n[htmlTag TR $row 1]
  #------------ I000 ----------------
  set    row	   [htmlTag TD I000]
    append row	 \n[htmlTag TD $PV($XREF(scaler_I000)) 0 $bkg]
    append row	 \n[htmlTag TD [format %.4f $PV($XREF(I000_VDC))]]
    append row	 \n[htmlTag TD [format %.1e $PV($XREF(I000_amp_gain))]]
    if {$PV($XREF(I000_amp_gain)) > 0} {
      set current [expr -1.0*$PV($XREF(I000_VDC)) / $PV($XREF(I000_amp_gain))]
    } else {
      set current 0
    }
    append row	 \n[htmlTag TD [format %e $current]]
    append rows  \n[htmlTag TR $row 1]
  #------------ photodiode ----------------
  set    row	   [htmlTag TD photodiode]
    append row	 \n[htmlTag TD $PV($XREF(scaler_diode)) 0 $bkg]
    append row	 \n[htmlTag TD [format %.4f $PV($XREF(diode_VDC))]]
    set gain $PV($XREF(diode_amp_gain))
    append row	 \n[htmlTag TD [format %.1e $gain]]
    set current $upd2_current   ;# 2006-06-06,PRJ: temporary substitute variable
    append row	 \n[htmlTag TD [format %e $current]]
    append rows  \n[htmlTag TR $row 1]
  set table        [htmlTag TABLE [string trim $rows] 1 BORDER=2]
  set    html(detectorBlock) [htmlTag H4 detectors]
    switch -- $PV($XREF(scaler_cnt)) {
      Done {}
      default {
        set    message "counting $PV($XREF(scaler_t))"
        append message " of $PV($XREF(scaler_tp)) seconds"
        append html(detectorBlock) \n[htmlTag SMALL $message]<BR>\n
      }
    }
  append html(detectorBlock) $table
  #append body \n[htmlTag BR]
  #append body \n$html(detectorBlock)
  #
  set slitTable {
    slits			mm	mm	mm	mm
    {USAXS (h,v)(gap,center)}	uslith	uslitv	uslith0	uslitv0
    {white (r,l,t,b)}		wslitr	wslitl	wslitt	wslitb
  }
  catch {unset rows}
  set labelRow 1
  foreach line [split [string trim $slitTable] \r\n] {
    set row [htmlTag TD [lindex $line 0]]
    foreach item [lrange $line 1 end] {
      if {$labelRow} {
        append row \n[htmlTag TD $item]
      } else {
        if [string compare $item "-"] {
	  append row \n[htmlMotorValueInTable [findMotor $item]]
	} else {
	  append row \n$emptyCell
	}
      }
    }
    append rows  \n[htmlTag TR $row 1]
    set labelRow 0
  }
  set table           [htmlTag TABLE [string trim $rows] 0 {BORDER=2}]
  set html(slitBlock) [htmlTag H4 slits]
  ###	set hor [expr $PV([findMotor uslitr].RBV,value) + $PV([findMotor uslitl].RBV,value)]
  ###	set ver [expr $PV([findMotor uslitt].RBV,value)   + $PV([findMotor uslitb].RBV,value)]
  ###	set message	 "USAXS slit opening: $ver mm (v) x $hor mm (h)"
  ###	append html(slitBlock)   \n[htmlTag SMALL $message]<BR>
  append html(slitBlock)   \n$table
  append body \n[htmlTag BR]
  append body \n$html(slitBlock)
  #
  set    tags SRC=\"$tool(pltFile)\"
  append tags { ALT="plot of USAXS data" WIDTH=200}
  set plotImage  [htmlTag IMG "" 0 $tags]
  set    html(plot)   [htmlTag H4 "USAXS plot"]
  set    tags HREF=\"$tool(showPlot)\"
  append html(plot) \n[htmlTag A $plotImage 0 $tags]
  #append body \n[htmlTag HR]
  set	 row   ""
  #append row   [htmlTag TD $html(slitBlock)]
  append row \n[htmlTag TD $html(detectorBlock) 1]
  append row \n[htmlTag TD $html(plot) 1]
  append body \n[htmlTag TABLE [htmlTag TR $row 1] 1]
  append body \n$html(motorBlock)
  #
  append body \n[makeTagHTML BR]
  append body \n[makeTagHTML HR]
  set    text "This page created by Pete Jemian, "
  append text [makeTagHTML TT jemian@anl.gov].
  set mtime 0
  foreach fl $tool(sourceFiles) {
    set mt [file mtime $fl]
    if {$mt > $mtime} {set mtime $mt}
  }
  set modTime [clock format $mtime -format %c]
  append text "  Last modified: $modTime"
  append body \n[makeTagHTML SMALL $text]
  #
  #
  set html(body)   [htmlTag BODY  $body 1]
  #
  # HTML
  #
  set    html(html)  [htmlTag HTML $html(head)\n$html(body) 1]
  #
  # write the HTML
  #
  if [catch {write_file $tool(baseNFS)/$tool(htmlFile) $html(html)} caughtText] {
    puts "Error writing HTML file:\n$caughtText"
  }
  #
  #-----------------------------------------------------------------
}

proc cleanString str {
  return [string trim [join $str] \"]
}
