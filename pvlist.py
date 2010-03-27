########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

pvconfig = [
  ["SR_current", "S:SRcurrentAI", "APS storage ring current, mA", "%.2f"],
  ["Und_E", "ID32:Energy", "ID E, keV", "%.4f"],
  ["white_shtr_closed", "PA:32ID:A_SHTRS_CLOSED.VAL", "32ID white shutter closed"],
  ["mono_shtr_closed", "PA:32ID:B_SHTRS_CLOSED.VAL", "32ID mono shutter closed"],
  ["white_shtr_auto", "32idb:AShtr:Enable.RVAL", "32ID white shutter autoOpen"],
  ["mir_alldone", "32idbMIR:alldone", "Mirror eBrick motors moving"],
  ["mirr_X_rbv", "32idbMIR:m1.RBV", "motor mirror_X, mm", "%.3f"],
  ["DCM_E", "32ida:BraggEAO", "DCM E, keV", "%.4f"],
  ["DCM_theta", "32ida:m1.RBV", "motor DCM_theta, degrees", "%.6f"],
  ["DCM_chi2", "32ida:m3.RBV", "motor DCM_chi2, degrees", "%.6f"],
  ["usx_alldone", "32idbUSX:alldone", "USAXS eBrick motors moving"],
  ["A2Rp_rbv", "32idbUSX:ath01:ana01:ai01.VAL", "pzt A2Rp, VDC, readback", "%.4f"],
  ["M2Rp_rbv", "32idbUSX:ath01:ana01:ai02.VAL", "pzt M2Rp, VDC, readback", "%.4f"],
  ["ASRp_rbv", "32idbUSX:ath01:ana01:ai03.VAL", "pzt ASRp, VDC, readback", "%.4f"],
  ["MSRp_rbv", "32idbUSX:ath01:ana01:ai04.VAL", "pzt MSRp, VDC, readback", "%.4f"],
  ["I0_VDC", "32idbUSX:ath01:ana01:ai05.VAL", "ADC I0, VDC", "%.4f"],
  ["I00_VDC", "32idbUSX:ath01:ana01:ai06.VAL", "ADC I00, VDC", "%.4f"],
  ["I000_VDC", "32idbMIR:ath01:ana01:ai01.VAL", "ADC I000, VDC", "%.4f"],
  ["diode_VDC", "32idbUSX:ath01:ana01:ai07.VAL", "ADC diode, VDC", "%.4f"],
  ["diode_amp_gain", "32idbUSX:fem01:seq01:gain", "PD amplifier gain V/A", "%.2e"],
  ["I0_amp_gain", "32idbUSX:fem02:seq01:gain", "I0 amplifier gain V/A", "%.2e"],
  ["I00_amp_gain", "32idbUSX:fem03:seq01:gain", "I00 amplifier gain, V/A", "%.2e"],
  ["I000_amp_gain", "32idbMIR:fem01:seq01:gain", "I000 amplifier gain, V/A", "%.2e"],
  ["PD_amp_gain", "32idbUSX:pd01:seq01:gain", "PD amplifier diode gain, V/A", "%.2e"],
  ["diode_count_rate", "32idbUSX:pd01:seq01:lurate", "diode count rate (at last update), c/s"],
  ["pf4_thickness_Al", "32idbUSX:pf4:filterAl", "filter Al thickness in beam, mm", "%.3f"],
  ["pf4_thickness_Ti", "32idbUSX:pf4:filterTi", "filter Ti thickness in beam, mm", "%.3f"],
  ["pf4_thickness_Gl", "32idbUSX:pf4:filterGlass", "filter glass thickness in beam, mm", "%.3f"],
  ["pf4_trans", "32idbUSX:pf4:trans", "filter transmission", "%.4e"],
  ["CCD_shtr_closed", "32idbUSX:pmm01:reg01:bo01", "shutter closed, USAXS CCD"],
  ["A2Rp_rbv", "32idbUSX:pzt:m1.RBV", "motor A2RP, VDC", "%.4f"],
  ["M2Rp_rbv", "32idbUSX:pzt:m2.RBV", "motor M2RP, VDC", "%.4f"],
  ["A2Rp_VDC", "32idbUSX:rmm01:ana01:ao01.VAL", "pzt A2Rp, VDC", "%.4f"],
  ["M2Rp_VDC", "32idbUSX:rmm01:ana01:ao02.VAL", "pzt M2Rp, VDC", "%.4f"],
  ["ASRp_VDC", "32idbUSX:rmm01:ana01:ao03.VAL", "pzt ASRp, VDC", "%.4f"],
  ["MSRp_VDC", "32idbUSX:rmm01:ana01:ao04.VAL", "pzt MSRp, VDC", "%.4f"],
  ["Ti_shtr_open", "32idbUSX:rmm02:reg01:bo08", "shutter open, USAXS Ti filter"],
  ["scaler_cnt", "32idbUSX:scaler1.CNT", "scaler counting time, s", "%.3f"],
  ["scaler_I0", "32idbUSX:scaler1.S2", "scaler I0, counts", "%d"],
  ["scaler_I00", "32idbUSX:scaler1.S3", "scaler I00, counts", "%d"],
  ["scaler_I000", "32idbUSX:scaler1.S5", "scaler I000, counts", "%d"],
  ["scaler_diode", "32idbUSX:scaler1.S4", "scaler diode, counts", "%d"],
  ["scaler_tp", "32idbUSX:scaler1.TP", "scaler counting time preset, s", "%.3f"],
  ["scaler_t", "32idbUSX:scaler1.T", "scaler counting time elasped, s", "%.3f"],
  ["lax_alldone", "32idbLAX:alldone", "LAX motors moving"],
  ["mr_enc", "32idbLAX:mr:encoder", "motor MR encoder, degrees", "%.6f"],
  ["m1y", "32idbLAX:m58:c0:m1.RBV", "motor M1Y, mm", "%.3f"],
  ["msx", "32idbLAX:m58:c0:m4.RBV", "motor MSX, mm", "%.3f"],
  ["msy", "32idbLAX:m58:c0:m5.RBV", "motor MSY, mm", "%.3f"],
  ["mx", "32idbLAX:m58:c0:m6.RBV", "motor MX, mm", "%.3f"],
  ["my", "32idbLAX:m58:c0:m7.RBV", "motor MY, mm", "%.3f"],
  ["msr", "32idbLAX:m58:c0:m8.RBV", "motor MSR, degrees", "%.6f"],
  ["asx", "32idbLAX:m58:c1:m4.RBV", "motor ASX, mm", "%.3f"],
  ["asy", "32idbLAX:m58:c1:m5.RBV", "motor ASY, mm", "%.3f"],
  ["ax", "32idbLAX:m58:c1:m6.RBV", "motor AX, mm", "%.3f"],
  ["ay", "32idbLAX:m58:c1:m7.RBV", "motor AY, mm", "%.3f"],
  ["az", "32idbLAX:m58:c1:m8.RBV", "motor AZ, mm", "%.3f"],
  ["sx", "32idbLAX:m58:c2:m1.RBV", "motor SX, mm", "%.3f"],
  ["sy", "32idbLAX:m58:c2:m2.RBV", "motor SY, mm", "%.3f"],
  ["dx", "32idbLAX:m58:c2:m4.RBV", "motor DX, mm", "%.3f"],
  ["dy", "32idbLAX:m58:c2:m5.RBV", "motor DY, mm", "%.3f"],
  ["asr", "32idbLAX:m58:c2:m8.RBV", "motor ASR, degrees", "%.6f"],
  ["uslitv0", "32idbLAX:m58:c3:m1.RBV", "motor uslitv0 USAXS slit vertical center, mm", "%.4f"],
  ["uslitv", "32idbLAX:m58:c3:m3.RBV", "motor uslitv USAXS slit vertical gap, mm", "%.4f"],
  ["uslith0", "32idbLAX:m58:c3:m2.RBV", "motor uslith0 USAXS slit horizontal center, mm", "%.4f"],
  ["uslith", "32idbLAX:m58:c3:m4.RBV", "motor uslith USAXS slit horizontal gap, mm", "%.4f"],
  ["wslitl", "32idb:m1.RBV", "motor wslitl white slit left, mm", "%.4f"],
  ["wslitb", "32idb:m2.RBV", "motor wslitb white slit bottom, mm", "%.4f"],
  ["wslitr", "32idb:m3.RBV", "motor wslitr white slit right, mm", "%.4f"],
  ["wslitt", "32idb:m4.RBV", "motor wslitt white slit top, mm", "%.4f"],
  ["mr", "32idbLAX:m58:c4:m1.RBV", "motor MR, degrees", "%.6f"],
  ["m1t", "32idbLAX:m58:c4:m2.RBV", "motor M1T, degrees", "%.4f"],
  ["mst", "32idbLAX:m58:c4:m4.RBV", "motor MST, degrees", "%.4f"],
  ["ar", "32idbLAX:m58:c5:m1.RBV", "motor AR, degrees", "%.6f"],
  ["ast", "32idbLAX:m58:c5:m4.RBV", "motor AST, degrees", "%.4f"],
  ["USAXS_I", "32idbLAX:USAXS:I", "I, a.u.", "%.4e"],
  ["USAXS_Q", "32idbLAX:USAXS:Q", "|Q|, 1/A", "%.4e"],
  ["SAD", "32idbLAX:USAXS:SAD", "sample-analyzer distance, mm", "%.1f"],
  ["SDD", "32idbLAX:USAXS:SDD", "sample-detector distance, mm", "%.1f"],
  ["sampleTitle", "32idbLAX:USAXS:sampleTitle", "SPEC sample title"],
  ["spec_macro_file", "32idbLAX:string19", "SPEC macro file"],
  ["timeStamp", "32idbLAX:USAXS:timeStamp", "USAXS macro timeStamp"],
  ["spec_dir", "32idbLAX:USAXS:userDir", "SPEC data directory"],
  ["spec_data_file", "32idbLAX:USAXS:specFile", "SPEC data file"],
  ["spec_scan", "32idbLAX:USAXS:specScan", "SPEC scan number"],
  ["state", "32idbLAX:USAXS:state", "SPEC what is happening?"],
  ["USAXS_collecting", "32idbLAX:bit19.VAL", "USAXS collecting data"],
  ["mirror_rh_pos", "32idbMIR:seq01:rh:inpos.RVAL", "USAXS mirror Rh stripe selected"],
  ["mirror_cr_pos", "32idbMIR:seq01:cr:inpos.RVAL", "USAXS mirror Cr stripe selected"],
  ["mirror_si_pos", "32idbMIR:seq01:si:inpos.RVAL", "USAXS mirror Si stripe selected"],
  ["mirror_wh_pos", "32idbMIR:seq01:wht:inpos.RVAL", "USAXS mirror white beam position selected"],
  ["mirr_x", "32idbMIR:m1.RBV", "motor mirror X, mm", "%.3f"],
  ["mirr_vs", "32idbMIR:m2.RBV", "motor mirror vertical steering, mm", "%.3f"],
  ["tcam", "32idbLAX:m58:c0:m3.RBV", "motor tcam position, degrees", "%.1f"],

  ["mirr_X_dmov", "32idbMIR:m1.DMOV", "motor done moving mirror_X"],
  ["DCM_theta_dmov", "32ida:m1.DMOV", "motor done moving DCM_theta"],
  ["DCM_chi2_dmov", "32ida:m3.DMOV", "motor done moving DCM_chi2"],
  ["A2Rp_dmov", "32idbUSX:pzt:m1.DMOV", "motor done moving A2RP"],
  ["M2Rp_dmov", "32idbUSX:pzt:m2.DMOV", "motor done moving M2RP"],
  ["m1y_dmov", "32idbLAX:m58:c0:m1.DMOV", "motor done moving M1Y"],
  ["msx_dmov", "32idbLAX:m58:c0:m4.DMOV", "motor done moving MSX"],
  ["msy_dmov", "32idbLAX:m58:c0:m5.DMOV", "motor done moving MSY"],
  ["mx_dmov", "32idbLAX:m58:c0:m6.DMOV", "motor done moving MX"],
  ["my_dmov", "32idbLAX:m58:c0:m7.DMOV", "motor done moving MY"],
  ["msr_dmov", "32idbLAX:m58:c0:m8.DMOV", "motor done moving MSR"],
  ["asx_dmov", "32idbLAX:m58:c1:m4.DMOV", "motor done moving ASX"],
  ["asy_dmov", "32idbLAX:m58:c1:m5.DMOV", "motor done moving ASY"],
  ["ax_dmov", "32idbLAX:m58:c1:m6.DMOV", "motor done moving AX"],
  ["ay_dmov", "32idbLAX:m58:c1:m7.DMOV", "motor done moving AY"],
  ["az_dmov", "32idbLAX:m58:c1:m8.DMOV", "motor done moving AZ"],
  ["sx_dmov", "32idbLAX:m58:c2:m1.DMOV", "motor done moving SX"],
  ["sy_dmov", "32idbLAX:m58:c2:m2.DMOV", "motor done moving SY"],
  ["dx_dmov", "32idbLAX:m58:c2:m4.DMOV", "motor done moving DX"],
  ["dy_dmov", "32idbLAX:m58:c2:m5.DMOV", "motor done moving DY"],
  ["asr_dmov", "32idbLAX:m58:c2:m8.DMOV", "motor done moving ASR"],
  ["uslitv0_dmov", "32idbLAX:m58:c3:m1.DMOV", "motor done moving uslitv0 USAXS slit vertical center"],
  ["uslitv_dmov", "32idbLAX:m58:c3:m3.DMOV", "motor done moving uslitv USAXS slit vertical gap"],
  ["uslith0_dmov", "32idbLAX:m58:c3:m2.DMOV", "motor done moving uslith0 USAXS slit horizontal center"],
  ["uslith_dmov", "32idbLAX:m58:c3:m4.DMOV", "motor done moving uslith USAXS slit horizontal gap"],
  ["wslitl_dmov", "32idb:m1.DMOV", "motor done moving wslitl white slit left"],
  ["wslitb_dmov", "32idb:m2.DMOV", "motor done moving wslitb white slit bottom"],
  ["wslitr_dmov", "32idb:m3.DMOV", "motor done moving wslitr white slit right"],
  ["wslitt_dmov", "32idb:m4.DMOV", "motor done moving wslitt white slit top"],
  ["mr_dmov", "32idbLAX:m58:c4:m1.DMOV", "motor done moving MR"],
  ["m1t_dmov", "32idbLAX:m58:c4:m2.DMOV", "motor done moving M1T"],
  ["mst_dmov", "32idbLAX:m58:c4:m4.DMOV", "motor done moving MST"],
  ["ar_dmov", "32idbLAX:m58:c5:m1.DMOV", "motor done moving AR"],
  ["ast_dmov", "32idbLAX:m58:c5:m4.DMOV", "motor done moving AST"],
  ["mirr_x_dmov", "32idbMIR:m1.DMOV", "motor done moving mirror X"],
  ["mirr_vs_dmov", "32idbMIR:m2.DMOV", "motor done moving mirror vertical steering"],
  ["tcam_dmov", "32idbLAX:m58:c0:m3.DMOV", "motor done moving tcam position"],

  ["pd_current",  "32idbUSX:pd01:seq01:lucurrent", "photodiode last-update current, A", "%.3e"],
  ["pd_amp_current",  "32idbLAX:userCalc7", "photodiode computed current, A", "%.3e"],
  ["I0_amp_current", "32idbLAX:userCalc8", "I0 computed current, A", "%.3e"],
  ["I00_amp_current", "32idbLAX:userCalc9", "I00 computed current, A", "%.3e"],
  ["I000_amp_current", "32idbLAX:userCalc10", "I000 computed current, A", "%.3e"]
]
