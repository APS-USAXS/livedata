#!/usr/bin/tclsh
#
# set global Tcl arrays for USAXS livedata.tcl

proc setDefaultConfig args {
  global tool config_table
  array set tool {
    PVmethod         pvConnect
    PVmethodChoices  {pvConnect burtrb}
    burtrb	     /usr/local/epics/extensions/bin/Linux/burtrb
    burt-switches    -sdds
    burt-request     burt.req
    burt-sdds	     burt.sdds
    burt-log	     burt.log
    APSstatusPlot    http://www.aps.anl.gov/aod/blops/plots/smallStatusPlot.png
    baseNFS	     /home/joule/USAXS/www/livedata
    baseWWW	     http://usaxs.xor.aps.anl.gov/livedata
    scanLogURL       http://usaxs.xor.aps.anl.gov/livedata/scanLog/scanlog.xml
    webcam           http://usaxsqvs1.xor.aps.anl.gov
    webcam-long      http://usaxsqvs1.xor.aps.anl.gov/view/index.shtml
    statusFile       status.txt
    htmlFile	     index.html
    rawFile	     rawdata.txt
    pltFile	     livedata.png
    plotFormat       png
    ploticus         /home/joule/USAXS/bin/pl
    specmacro	     specmacro.txt
    rawDataURL       rawdata.txt
    showPlot	     showplot.html
    waitInterval_ms  5000
    htmlRefresh_s    300
    replotInterval_s 20
    nbsp	     &nbsp;
    title	     "32ID-B USAXS status"
    sourceFiles      {  
		      config.tcl
		      htmlTag.tcl
		      main.tcl
		      plot.tcl  
		      pvConnect.tcl
                      readSpecFile.tcl
		      tools.tcl  
		      wwwpage.tcl
		     }
  }

  # PV_desc
  set config_table {
    SR_current         S:SRcurrentAI		  {APS storage ring current, mA     }
    Und_E	       ID32:Energy		  {ID E, keV			    }
    white_shtr_closed  PA:32ID:A_SHTRS_CLOSED.VAL {32ID white shutter closed	    }
    mono_shtr_closed   PA:32ID:B_SHTRS_CLOSED.VAL {32ID mono shutter closed	    }
    white_shtr_auto    32idb:AShtr:Enable.RVAL    {32ID white shutter autoOpen	    }
    mir_alldone        32idbMIR:alldone		  {Mirror eBrick motors moving      }
    mirr_X_rbv         32idbMIR:m1.RBV		  {motor mirror_X, mm		    }
    DCM_E	       32ida:BraggEAO		  {DCM E, keV			    }
    DCM_theta	       32ida:m1.RBV		  {motor DCM_theta, degrees	    }
    DCM_chi2	       32ida:m3.RBV		  {motor DCM_chi2, degrees	    }
    usx_alldone        32idbUSX:alldone		  {USAXS eBrick motors moving	    }
    A2Rp_rbv	       32idbUSX:ath01:ana01:ai01.VAL	{pzt A2Rp, VDC, readback	    }
    M2Rp_rbv	       32idbUSX:ath01:ana01:ai02.VAL	{pzt M2Rp, VDC, readback	    }
    ASRp_rbv	       32idbUSX:ath01:ana01:ai03.VAL	{pzt ASRp, VDC, readback	    }
    MSRp_rbv	       32idbUSX:ath01:ana01:ai04.VAL	{pzt MSRp, VDC, readback	    }
    I0_VDC	       32idbUSX:ath01:ana01:ai05.VAL	{ADC I0, VDC  		    }
    I00_VDC	       32idbUSX:ath01:ana01:ai06.VAL	{ADC I00, VDC 		    }
    I000_VDC	       32idbMIR:ath01:ana01:ai01.VAL   {ADC I000, VDC 		    }
    diode_VDC	       32idbUSX:ath01:ana01:ai07.VAL   {ADC diode, VDC		    }
    diode_amp_gain     32idbUSX:fem01:seq01:gain       {PD amplifier gain V/A		 }
    I0_amp_gain        32idbUSX:fem02:seq01:gain       {I0 amplifier gain V/A		 }
    I00_amp_gain       32idbUSX:fem03:seq01:gain       {I00 amplifier gain, V/A 	 }
    I000_amp_gain      32idbMIR:fem01:seq01:gain       {I000 amplifier gain, V/A	 }
    PD_amp_gain        32idbUSX:pd01:seq01:gain	       {PD amplifier diode gain, V/A     }
    diode_count_rate   32idbUSX:pd01:seq01:lurate      {diode count rate (at last update), c/s  }
    pf4_thickness_Al   32idbUSX:pf4:filterAl	       {filter Al thickness in beam, mm  }
    pf4_thickness_Ti   32idbUSX:pf4:filterTi	       {filter Ti thickness in beam, mm  }
    pf4_thickness_Gl   32idbUSX:pf4:filterGlass        {filter glass thickness in beam, mm  }
    pf4_trans	       32idbUSX:pf4:trans	       {filter transmission 	     }
    CCD_shtr_closed    32idbUSX:pmm01:reg01:bo01       {shutter closed, USAXS CCD	    }
    A2Rp_rbv	       32idbUSX:pzt:m1.RBV	       {motor A2RP, VDC		    }
    M2Rp_rbv	       32idbUSX:pzt:m2.RBV	       {motor M2RP, VDC		    }
    A2Rp_VDC	       32idbUSX:rmm01:ana01:ao01.VAL   {pzt A2Rp, VDC		    }
    M2Rp_VDC	       32idbUSX:rmm01:ana01:ao02.VAL   {pzt M2Rp, VDC		    }
    ASRp_VDC	       32idbUSX:rmm01:ana01:ao03.VAL   {pzt ASRp, VDC		    }
    MSRp_VDC	       32idbUSX:rmm01:ana01:ao04.VAL   {pzt MSRp, VDC		    }
    Ti_shtr_open       32idbUSX:rmm02:reg01:bo08	  {shutter open, USAXS Ti filter    }
    scaler_cnt         32idbUSX:scaler1.CNT  	  {scaler counting time, s	    }
    scaler_I0	       32idbUSX:scaler1.S2	  {scaler I0, counts		    }
    scaler_I00         32idbUSX:scaler1.S3	  {scaler I00, counts		    }
    scaler_I000        32idbUSX:scaler1.S5	  {scaler I000, counts		    }
    scaler_diode       32idbUSX:scaler1.S4	  {scaler diode, counts 	    }
    scaler_tp	       32idbUSX:scaler1.TP	  {scaler counting time preset, s   }
    scaler_t	       32idbUSX:scaler1.T	  {scaler counting time elasped, s  }
    lax_alldone        32idbLAX:alldone		  {LAX motors moving		    }
    ar_enc	       32idbLAX:ar:encoder	  {motor AR encoder, degrees	    }
    mr_enc	       32idbLAX:mr:encoder	  {motor MR encoder, degrees	    }
    m1y 	       32idbLAX:m58:c0:m1.RBV	  {motor M1Y, mm		    }
    msx 	       32idbLAX:m58:c0:m4.RBV	  {motor MSX, mm		    }
    msy 	       32idbLAX:m58:c0:m5.RBV	  {motor MSY, mm		    }
    mx  	       32idbLAX:m58:c0:m6.RBV	  {motor MX, mm 		    }
    my  	       32idbLAX:m58:c0:m7.RBV	  {motor MY, mm 		    }
    msr 	       32idbLAX:m58:c0:m8.RBV	  {motor MSR, degrees		    }
    asx 	       32idbLAX:m58:c1:m4.RBV	  {motor ASX, mm		    }
    asy 	       32idbLAX:m58:c1:m5.RBV	  {motor ASY, mm		    }
    ax  	       32idbLAX:m58:c1:m6.RBV	  {motor AX, mm 		    }
    ay  	       32idbLAX:m58:c1:m7.RBV	  {motor AY, mm 		    }
    az  	       32idbLAX:m58:c1:m8.RBV	  {motor AZ, mm 		    }
    sx  	       32idbLAX:m58:c2:m1.RBV	  {motor SX, mm 		    }
    sy  	       32idbLAX:m58:c2:m2.RBV	  {motor SY, mm 		    }
    dx  	       32idbLAX:m58:c2:m4.RBV	  {motor DX, mm 		    }
    dy  	       32idbLAX:m58:c2:m5.RBV	  {motor DY, mm 		    }
    asr 	       32idbLAX:m58:c2:m8.RBV	  {motor ASR, degrees		    }
    uslitv0	       32idbLAX:m58:c3:m1.RBV	  {motor uslitv0 USAXS slit vertical center, mm  }
    uslitv	       32idbLAX:m58:c3:m3.RBV	  {motor uslitv USAXS slit vertical gap, mm	    }
    uslith0	       32idbLAX:m58:c3:m2.RBV	  {motor uslith0 USAXS slit horizontal center, mm   }
    uslith	       32idbLAX:m58:c3:m4.RBV	  {motor uslith USAXS slit horizontal gap, mm	    }
    wslitl	       32idb:m1.RBV	  	  {motor wslitl white slit left, mm  }
    wslitb	       32idb:m2.RBV	  	  {motor wslitb white slit bottom, mm  }
    wslitr	       32idb:m3.RBV	  	  {motor wslitr white slit right, mm  }
    wslitt	       32idb:m4.RBV	  	  {motor wslitt white slit top, mm  }
    mr  	       32idbLAX:m58:c4:m1.RBV	  {motor MR, degrees		    }
    m1t 	       32idbLAX:m58:c4:m2.RBV	  {motor M1T, degrees		    }
    mst 	       32idbLAX:m58:c4:m4.RBV	  {motor MST, degrees		    }
    ar  	       32idbLAX:m58:c5:m1.RBV	  {motor AR, degrees		    }
    ast 	       32idbLAX:m58:c5:m4.RBV	  {motor AST, degrees		    }
    USAXS_I	       32idbLAX:USAXS:I		  {I, a.u.			    }
    USAXS_Q	       32idbLAX:USAXS:Q		  {|Q|, 1/A			    }
    SAD 	       32idbLAX:USAXS:SAD	  {sample-analyzer distance, mm     }
    SDD 	       32idbLAX:USAXS:SDD	  {sample-detector distance, mm     }
    sampleTitle        32idbLAX:USAXS:sampleTitle {SPEC sample title		    }
    spec_macro_file    32idbLAX:string19	  {SPEC macro file		    }
    timeStamp	       32idbLAX:USAXS:timeStamp	  {USAXS macro timeStamp	    }
    spec_dir	       32idbLAX:USAXS:userDir	  {SPEC data directory  	    }
    spec_data_file     32idbLAX:USAXS:specFile	  {SPEC data file		    }
    spec_scan	       32idbLAX:USAXS:specScan	  {SPEC scan number		    }
    state	       32idbLAX:USAXS:state  	  {SPEC what is happening?	    }
    USAXS_collecting   32idbLAX:bit19.VAL	  {USAXS collecting data	    }
    mirror_rh_pos      32idbMIR:seq01:rh:inpos.RVAL  {USAXS mirror Rh stripe selected}
    mirror_cr_pos      32idbMIR:seq01:cr:inpos.RVAL  {USAXS mirror Cr stripe selected}
    mirror_si_pos      32idbMIR:seq01:si:inpos.RVAL  {USAXS mirror Si stripe selected}
    mirror_wh_pos      32idbMIR:seq01:wht:inpos.RVAL {USAXS mirror white beam position selected}
    mirr_x 	       32idbMIR:m1.RBV	  	  {motor mirror X, mm		    }
    mirr_vs 	       32idbMIR:m2.RBV	  	  {motor mirror vertical steering, mm	}
    tcam 	       32idbLAX:m58:c0:m3.RBV	  {motor tcam position, degrees	}
  }
}

set ignore {
}

proc readConfig args {
  global Description  XREF  PV  config_table
  catch {unset pvList}
  setDefaultConfig
  foreach {var pv desc} $config_table {
    set Description($var) [string trim $desc]
    set XREF($var) $pv
    set PV($pv) "***not-connected***"
    lappend pvList $pv
    #--- Now check if the PV is for a motor record
    set pos [string first .RBV $pv]
    if {$pos >= 0} {
      set pvBase [string range $pv 0 [incr pos -1]]
      set pv $pvBase.DMOV
      set pos [string first _rbv $var]
      if {$pos > 0} {
        incr pos -1
        set var [string range $var 0 $pos]
      }
      append var _dmov
      set desc "$var done moving"
      set desc "$var done moving"
      set XREF($var) $pv
      set PV($pv) "***not-connected***"
      lappend pvList $pv
    }
  }
  return $pvList
}
