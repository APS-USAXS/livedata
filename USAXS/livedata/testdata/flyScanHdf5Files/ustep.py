#!/usr/bin/env python

'''
Step-Size Algorithm for Bonse-Hart Ultra-Small-Angle Scattering Instruments

:see: http://usaxs.xray.aps.anl.gov/docs/ustep/index.html
'''


import math


def ustep(start, center, finish, numPts, factor, exponent, minStep):
    '''
    return a list of positions between start and finish
    
    :param float start: required first position of list
    :param float center: position to take minStep
    :param float finish: required ending position of list
    :param float numPts: length of the list
    :param float factor: :math:`k`, multiplying factor
    :param float exponent: :math:`\eta`, exponential factor
    :param float minStep: smallest allowed step size
    '''
# def uascanTestSeries(start, center, finish, numPts, factor, exponent, minStep) '{
#   local x step i dir
# 
#   x = start
#   dir = (start < finish) ? 1 : -1
#   for (i=1; i < numPts; i++) {
#     step = uascanStepFunc(x, factor, center, exponent, minStep)
#     x += dir*step
#     if ( ((dir>0) && (x > finish))  ||  ((dir<0) && (x < finish)) ) {
#       return i
#     }
#   }
#   return (-1 * fabs(x - finish))
# }'
    pass


def main():
    pass


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

# SPEC implementation
'''
#
#  usaxs_uascan.mac
#
#  USAXS-specific macros
#  maintained by Jan Ilavsky
#  last edit:  2012-10-17
#
########### SVN repository information ###################
# :HeadURL: https://subversion.xray.aps.anl.gov/spec/beamline_config/trunk/usaxs/usaxs/usaxs_uascan.mac
########### SVN repository information ###################


#  globals:
# these numbers should be mostly set in USAXS_conf.mac or other configuration file...

global     ARenc_CENTER                  # AR center in encoder value... Probably not needed anymore
global     SPEC_STD_TITLE                # scan title


# these are now epics variables
#global     AR_VAL_CENTER                 # center value for AR stage
#global     NUMPTS                        # number of points
#global     UATERM                        # weighing value... Changes spread of the log stepping
#global     START_OFFSET                  # Q offset to start above AR_VAL_CENTER
#global     FINISH                        # end angle for USAXS scans
#global     USAXS_MINSTEP                 # min step of uascan
#
#
#  ASRP calibration.
  ASRP_DEGREES_PER_VDC = 0.0059721     # measured by JI October 9, 2006 during setup at 32ID. Std Dev 4e-5
#######
#############################################################################
#############################################################################
#############################################################################
###################################################################################
###################################################################################
####
####  general scan macro for USAXS for both 1D & 2D collimations
####
def USAXSscan '{
  local pos_X pos_Y scan_title Finish_in_Angle _USAXS_Lambda

  global ARenc_CENTER
  global SPEC_STD_TITLE
  global USAXS_SAMPLE_THICKNESS
  global useSBUSAXS
  global USAXS_MEASURE_DARK_CURENTS
  global USAXSScanUp

  if( $# != 4) {
    printf ("USAXSscan pos_X pos_Y thickness_mm scan_title\n");
    exit;
  }
  pos_X = $1
  pos_Y = $2
  USAXS_SAMPLE_THICKNESS = $3
  scan_title = __returnSampleName("$4")
  ## clean the user name
  scan_title  = __get_clean_user_string(scan_title)

  # need to check pos_X and pos_Y against soft limits before proceeding
  _bad_lim = 0
  _chk_lim sx pos_X
  _chk_lim sy pos_Y
  if (_bad_lim) {
    printf("sample position (%.3f,%.3f) exceeds soft limits\n", pos_X, pos_Y)
    exit;
  }
    # make sure we are in USAXS mode, cannot run otherwise.
  useModeUSAXS

  SPEC_STD_TITLE = TITLE
  TITLE      = scan_title

  epics_put ("15iddLAX:USAXS:sampleTitle", scan_title)
  epics_put ("15iddLAX:USAXS:state",       sprintf("USAXS count time: %g seconds", USAXS_TIME))
  epics_put ("15iddLAX:USAXS:userName",    USER)
  epics_put ("15iddLAX:USAXS:userDir",     CWD)
  epics_put ("15iddLAX:USAXS:specFile",    DATAFILE)
  epics_put ("15iddLAX:USAXS:specScan",    SCAN_N+1)
  if (useSBUSAXS) {
    epics_put ("15iddLAX:USAXS:scanMacro",   "sbuascan")
  } else {
    epics_put ("15iddLAX:USAXS:scanMacro",   "uascan")
  }
  epics_put ("15iddLAX:USAXS:timeStamp",   date())

  set_USAXS_Slits                # make sure USAXS slits are set correctly...

  comment "Moving AR motor to %g degrees (beam center)" AR_VAL_CENTER
  A[ar] = AR_VAL_CENTER
  waitmove; get_angles;
  ARenc_CENTER = A[ar]
  comment "for next scan: encoder ARenc_CENTER  = %7.4f" ARenc_CENTER
     # Set the center for the Q calculation for plotting here
  epics_put("15iddLAX:USAXS:Q.B", ARenc_CENTER-0.00005)

  MINSTEP    = USAXS_MINSTEP    # JI 10 26 2006 change to allow user specified min step
  TIME       = USAXS_TIME
  epics_put ("15iddLAX:USAXS:state",       "moving sample into beam")
  moveSample pos_X pos_Y
  #Calculate Finish in angle, since now it is in Q units
  #use en as energy in keV,
  _USAXS_Lambda = 12.4 / A[en]
  # decide if we are scaning up or down...
  if(USAXSScanUp) {
        # scanning up, new method
        Finish_in_Angle = AR_VAL_CENTER + (360/PI)*asin( FINISH * _USAXS_Lambda / (4*PI))
        # START = AR_VAL_CENTER - START_OFFSET
        # 2013-2-9 Changed to START_OFFSET in Q and need negative value to start above/below the peak now.
        START = AR_VAL_CENTER + (360/PI)*asin( START_OFFSET * _USAXS_Lambda / (4*PI))
  } else {
        # scanning down, old method
        Finish_in_Angle = AR_VAL_CENTER - (360/PI)*asin( FINISH * _USAXS_Lambda / (4*PI))
        #START = AR_VAL_CENTER + START_OFFSET
        # 2013-2-9 Changed to START_OFFSET in Q and need negative value to start above/below the peak now.
        START = AR_VAL_CENTER - (360/PI)*asin( START_OFFSET * _USAXS_Lambda / (4*PI))
  }
  # measure transmission values using pin diode if desired (added 4-12-2013)
  measure_USAXS_PinT

  # cleanup macro for ^C usage
  rdef _cleanup3 \'resetUSAXS\'

  epics_put ("15iddLAX:USAXS:state",       "starting USAXS scan")

  comment "uascan started"

  uascan ar START AR_VAL_CENTER Finish_in_Angle MINSTEP DY0 SDD AY0 SAD UATERM NUMPNTS TIME

  comment "uascan finished"


  if (USAXS_MEASURE_DARK_CURENTS) {
      epics_put ("15iddLAX:USAXS:state",       "measuring dark currents")
      measure_USAXS_PD_dark_currents
  }

  comment "Moving AR motor back to %g degrees (beam center)" AR_VAL_CENTER
  mv ar AR_VAL_CENTER
  waitmove; get_angles
  if(fabs(A[ar]-AR_VAL_CENTER)>0.0001){
     comment "AR failed to return to the correct position, attempting to fix it"
     sleep(1)
     umvr ar 0.001
     waitmove; get_angles
     umv ar AR_VAL_CENTER
     waitmove; get_angles
  }


  # normal cleanup macro for ^C usage
  rdef _cleanup3 \'\'
  comment %s scan_title
  TITLE = SPEC_STD_TITLE
  epics_put ("15iddLAX:USAXS:state",       "scan finished")
}'

####################################################
#########   Measure pindiode transmission in USAXS
####################################################

def measure_USAXS_PinT'
  #global USAXS_MEASURE_PIN_TRANS
  epics_put ("15iddLAX:USAXS:state",       "Measuring USAXS transmission")
  if(USAXS_MEASURE_PIN_TRANS){
     useModeUSAXS
     waitmove; get_angles
     mv ay (USAXSPinT_AyPosition)
     waitmove; get_angles
     openTiFilterShutter
     autorange_UPDI0I00
     #epics_put("15iddUSX:fem03:seq01:gainidx",8)
     ct USAXSPinT_MeasurementTime
     closeTiFilterShutter
     mv ay AY0
     epics_put("15iddLAX:vsc:c0.TP",USAXSPinT_MeasurementTime)
     set_USAXSPinT_pinCounts  epics_get("15iddLAX:vsc:c0.S3")
     set_USAXSPinT_pinGain    epics_get("15iddUSX:fem03:seq01:gain")
     set_USAXSPinT_I0Counts   epics_get("15iddLAX:vsc:c0.S2")
     set_USAXSPinT_I0Gain     epics_get("15iddUSX:fem02:seq01:gain")
     printf ("Measured USAXS transmission values pinDiode cts =%f with gain %g and  I0 cts =%f with gain %g\n", USAXSPinT_pinCounts, USAXSPinT_pinGain, USAXSPinT_I0Counts,USAXSPinT_I0Gain);
     waitmove; get_angles
  }else{
     set_USAXSPinT_pinCounts  0
     set_USAXSPinT_pinGain    0
     set_USAXSPinT_I0Counts   0
     set_USAXSPinT_I0Gain     0
     printf ("Did not measure USAXS transmission \n");
 }
'

####################################################
##### resetUSAXS macro
####################################################

def resetUSAXS '{
  global SPEC_STD_TITLE
  global useSBUSAXS
  global NOTIFY_ON_RESET
  comment "Resetting USAXS"
  epics_put ("15iddLAX:USAXS:state",       "resetting motors")
  setplot 131
  # start feedback
  DCMfeedbackON
  # turn on the AutoCount mode on the scaler
  epics_put(sprintf("%s.CONT",_SCALER_PV), "1") #from jfk
  # turn on the photodiode to auto+bkg mode. I0 and I00 to manual mode
  modeAutoBRange_UPD
  modeManualRange_I0
  modeManualRange_I00
  # close the shutter after each scan to preserve the detector
  closeTiFilterShutter
  # clear the user bit to indicate USAXS scan is not running
  epics_put ("15iddLAX:USAXS:scanning",  0)
     waitmove; get_angles
     A[dy] = DY0
     A[ay] = AY0
     A[ar] = AR_VAL_CENTER
     if(useSBUSAXS){
       A[asrp] = ASRP0
     }
     move_em; waitmove
  TITLE = SPEC_STD_TITLE
  epics_put (sprintf("15iddUSX:%s:mode",PDstring), 2)
  epics_put (sprintf("%s.CONT",_SCALER_PV), 1) #from jfk:vsc:c0 -xjiao
  epics_put ("15iddLAX:USAXS:state",       "USAXS reset complete")
  if(NOTIFY_ON_RESET) { sendNotifications("USAXS has reset","spec has encountered a problem and reset the USAXS.");}
  chk_beam_off
  rdef _cleanup3 \'\'
}'

#############################################################################
#############################################################################
#############################################################################
#
#  uascan scans the one motor (AR assumed).
#  (uascan stands for USAXS ascan, incorporating a step
#  size that varies with distance from a center point.)
#########################################################################
#
# `uascan' is a single-motor scan with adjustable step size
#
def uascan '
  if ($# != 12) {
    printf("Usage: uascan %s %s %s\n",         \
       "motor start center finish minStep",    \
       "dy0 SDD_mm ay0 SAD_mm",                \
       "exponent intervals time")
    exit
  }
  local _s
  local _f
  local _d
  local _center
  local _asrp0

         # read header into internal (local) parameters.
         # Do they have to be declared local or global or just left as is?
  _s = $2; _center = $3; _f = $4; _ms = $5
  _dy0    = $6;
  SAMPLE_DETECTOR_DISTANCE_MM = $7;
  _ay0    = $8;
  SAMPLE_ANALYZER_DISTANCE_MM = $9;
  _exp    = $10
  _n1     = int($11)
  _ctime  = $12
  _ctime_base = _ctime

  if(useDynamicTime)
  {
      _ctime = _ctime_base / 3
  }
  if(useIntelligentTime)
  {   
    _ctime = CT_RANGE_1
  }
        # end of reading the header

        # declare variables to store current values...
    local old_dy              # position of photodiode before scan
    local old_ay              # position of AY before scan
    local old_sy              # position of SY before scan
    local old_ar              # position of AR motor before scan
    local old_ASRP            # position of ASRP motor before scan

        # check some basic conditions   
      if (_n1 <= 0) {
        print "Intervals <= 0"
        exit
    }
     _bad_lim = 0
     _chk_lim ar _s
     _chk_lim ar _f
     if (_bad_lim) exit;

        # set heading for scans to show if we are running USAXS or SBUSAXS
    HEADING = (useSBUSAXS) ?  "sbuascan " : "uascan "
    HEADING=sprintf("%s%s",HEADING,sprintf(" %s %g %g %g %g ",\
        "ar",_s,_center,_f,_ms))
    HEADING=sprintf("%s %g %g",HEADING,_dy0,SAMPLE_DETECTOR_DISTANCE_MM)
    HEADING=sprintf("%s %g %g",HEADING,_ay0,SAMPLE_ANALYZER_DISTANCE_MM)
    HEADING=sprintf("%s %g %g %g",HEADING,_exp,_n1,_ctime)


         # find appropriate factor for weighing the points
    _d = uascanFindFactor(_s, _center, _f, _n1, _exp, _ms)
    _dir = (_s < _f) ? 1 : -1
         _n1++
    _cols=1
    X_L = motor_name(ar)
    Y_L = cnt_name(DET)
    _sx = _s; _fx = _f
    _stype = 1
    FPRNT=PPRNT=VPRNT=""
    FPRNT=sprintf("%s%s  ",FPRNT,motor_name(ar))
    PPRNT=sprintf("%s%8.8s ",PPRNT,motor_name(ar))
    VPRNT=sprintf("%s%9.9s ",VPRNT,motor_name(ar))
    scan_head
    PFMT=sprintf("%%s%%8.%df ",UP)
    VFMT=sprintf("%%s%%9.%df ",UP)
    # UP is user precision, defined in standard.mac as 4
        # it can be redefined to show more decimal places if needed

    # count the actual number of data points in this scan
    def _scan_on \'
      local scan_over
      scan_over = 0
             # _s is next point calculate during last point, or start angle from call to macro
      _pos = _s
     for (; NPTS < _n1; NPTS++) {
        local  target_sy   target_ay   target_dy
                 ### set Ar angle to target
        A[ar] = _pos

             ### re-position DY on the scattered beam
        target_dy = _dy0 + _usaxs_triangulate (A[ar], AR_VAL_CENTER, SAMPLE_DETECTOR_DISTANCE_MM)
        A[dy] = target_dy

             ### re-position AY on the scattered beam
        target_ay = _ay0 + _usaxs_triangulate (A[ar], AR_VAL_CENTER, SAMPLE_ANALYZER_DISTANCE_MM)
        A[ay] = target_ay

        target_sy = A[sy]
        if (NPTS > 0) {
                 ### (maybe) re-position the sample before each step after the first
          target_sy = A[sy] + SAMPLE_Y_STEP
              #p "moving sy to " target_sy
          A[sy] = target_sy
        }
                   ### ASRP stuff, more complicated...
            if(useSBUSAXS){
               ### adjust the ASRP piezo on the AS side-bounce stage
             tanBragg = tan(_center*PI/180)
             cosScatAngle = cos((_center-A[ar])*PI/180)
                    diff = atan(tanBragg/cosScatAngle)*180/PI - _center
                    # on 11 19 2003 the original (Pete) formula with sin replaced
                    # by Jan and Andrew with formulas using tan... Should be correct...
                    # this is original Petes formula .... diff = asin(sinBragg/cosScatAngle)*180/PI - _center
                #
                # Note on asrp adjustment:  NOTE: seems wrong, but may need to be revisited???
                #   use "-" when reflecting  inboard towards storage ring (single bounce setup)
                #   use "+" when reflecting outboard towards experimenters (channel-cut setup)
                ### on 2/06/2002 Andrew realized, that we are moving in wrong direction
                    ## the sign change to - moves ASRP towards larger Bragg angles...
                    ## verified experimentally - higher voltage on piezo = lower Bragg angle...
                ## and we need to INCREASE the Bragg Angle with increasing Q, to correct for tilt down...
                #######p "updating the piezo with" asrp_vdc
                ###old-style###epics_put (asrp_control_PV, asrp_vdc)
                 asrp_vdc = _asrp0 - diff/ASRP_DEGREES_PER_VDC
             A[asrp] = asrp_vdc
                 #######p "ASRP has been updated"
            }

                ### write comment for GUI
         epics_put ("15iddLAX:USAXS:state", sprintf("%s %d/%d", "moving motors", NPTS+1, _n1-1))
                   ### move to point
        scan_move
                   ### spec stuff
        FPRNT=PPRNT=VPRNT=""
           FPRNT=sprintf("%s%.8g ",FPRNT,A[ar])
          PPRNT=sprintf(PFMT,PPRNT,A[ar])
          VPRNT=sprintf(VFMT,VPRNT,A[ar])
                   ### write comment for GUI
            epics_put ("15iddLAX:USAXS:state", sprintf("%s %d/%d", "counting", NPTS+1, _n1-1))
               ### spec stuff...
            #added for fuel spray users as indication that we are counting...
            epics_put("15iddLAX:bit1",1)
            # end of fuel spray modification

        scan_loop
        scan_data(NPTS,A[ar])
        scan_plot

               ### calculate position for next step here
            _pos += _dir * uascanStepFunc(_pos, _d, _center, _exp, _ms)
                
        if(useDynamicTime){
            if(NPTS < (_n1/3)) { _ctime = _ctime_base / 2 }
            if(NPTS > (_n1/3) && NPTS < ((2/3)*_n1)) { _ctime = _ctime_base }
            if(NPTS > ((2/3)*_n1)) { _ctime = 2*_ctime_base}
        }

      if(useIntelligentTime) {
            updRange =epics_get(sprintf("%s:lurange",UPD_PV), "short")
            if(updRange==0)
            {
                    _ctime = CT_RANGE_1
            }
            else if(updRange == 1)
            {
                    _ctime = CT_RANGE_2
            }
            else if(updRange == 2)
            {
                    _ctime = CT_RANGE_3
            }
            else if(updRange == 3)
            {
                    _ctime = CT_RANGE_4
            }
            else
            {
                    _ctime = CT_RANGE_5
            }
      }
    
               ### check if done.
             if (_dir > 0) {
            if (_pos > _f) scan_over = 1
          } else {
            if (_pos < _f) scan_over = 1
          }
        if (scan_over == 1) break
     }
     scan_tail
    \'
       ### remember pre-scan motor positions: AY, SY, DY, and AR
    old_ay    = A[ay]
    old_sy    = A[sy]
    old_dy    = A[dy]
    old_ar    = A[ar]
      if(useSBUSAXS){
         old_ASRP   = A[asrp]
         _asrp0     = A[asrp]
      }
       # make the scaler wait before counting
    epics_put(sprintf("%s.DLY",_SCALER_PV), MOTOR_PRESCALER_WAIT)
       # turn off the AutoCount mode on the scaler
    epics_put(sprintf("%s.CONT",_SCALER_PV), "0")
         #  When using the USAXS_chk_beam macro,
         #  test for the "beam dumped" condition by
         #  setting a threshold on the I0 monitor counts.
         #  Specify here using a minimum I0 count rate.
      chk_thresh = _ctime * 2000
       # close the shutter just in case it is important
      closeTiFilterShutter
       # rotate AR (or MR) to the starting position
      epics_put ("15iddLAX:USAXS:state",       "rotate to first angle")
      waitmove; get_angles
      A[ar] = _s
      move_em; waitmove
       # open the shutters just before each scan to preserve the detector
      openTiFilterShutter
      openMonoShutter
              # set the photodiode on mid-range and put into auto mode

#epics_put(sprintf("15iddUSX:%s:reqrange.VAL",PDstring), 2);   
              #set_UPD_gain 8
              #epics_put(sprintf("15iddUSX:%s:mode.VAL",PDstring), 1);
        # autorange all amplifilers
      autorange_UPDI0I00
        # put the I0 and I00 to automatic mode, change JIL for 2012-03
      modeAutoRange_I0
      modeAutoRange_I00
        # this should end with all in manual mode, but UPD needs auto mode
      modeAutoRange_UPD
        # stop mono feedback if running
      DCMfeedbackOFF
        # set a bit to indicate USAXS scan is running
      if (useSBUSAXS) {
          epics_put ("15iddLAX:USAXS:scanMacro", "sbuascan")
      } else {
          epics_put ("15iddLAX:USAXS:scanMacro", "uascan")
      }
      epics_put ("15iddLAX:USAXS:scanning", 1)

    ###set plot method
      setplot 131             ;#  0 turns off plot during scan
    # run the scan itself...

    _scan_on

    ###------------------------
         # clear the user bit to indicate USAXS scan is not running
      epics_put ("15iddLAX:USAXS:scanning.VAL",  0)
       # start feedback
      DCMfeedbackON
       # turn on the AutoCount mode on the scaler
    epics_put(sprintf("%s.CONT",_SCALER_PV), "1") #from jfk
       # turn on the photodiode to auto+bkg mode. I0 and I00 to manual mode
      modeAutoBRange_UPD
      modeManualRange_I0
      modeManualRange_I00
       # close the shutter after each scan to preserve the detector
    closeTiFilterShutter
       # reset motors to pre-scan positions: AY, SY, DY, and "the first motor" (AR)
      epics_put ("15iddLAX:USAXS:state",       "returning AR, AY, SY, and DY")
        get_angles
        A[ay]    = old_ay
        A[sy]    = old_sy
        A[dy]    = old_dy
        A[ar]    = old_ar
          if(useSBUSAXS){
              A[asrp]  = old_ASRP
          }
        move_em; waitmove
'

#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#
#    subprograms....
#
# uascanStepFunc
#
# Calculate the next step size with the given parameters
#
uascanStepDebug = 0
def uascanStepFunc(x, factor, center, exponent, minStep) '{
  local step
  step = factor * pow( fabs(x - center), exponent ) + minStep
  if (uascanStepDebug >= 2)
    printf ("step = %g\n", step)
  return step
}'

# uascanTestSeries
#
# Make a series with the specified parameters
#  If factor is too large, return the number of points required to reach finish.
#  Otherwise, return the closeness of the final point to the finish.
#
def uascanTestSeries(start, center, finish, numPts, factor, exponent, minStep) '{
  local x step i dir

  x = start
  dir = (start < finish) ? 1 : -1
  for (i=1; i < numPts; i++) {
    step = uascanStepFunc(x, factor, center, exponent, minStep)
    x += dir*step
    if ( ((dir>0) && (x > finish))  ||  ((dir<0) && (x < finish)) ) {
      return i
    }
  }
  return (-1 * fabs(x - finish))
}'

# uascanFindFactor
#
# Determine the factor that will make a series with the specified parameters.
#  Choose the factor that will minimize | x[n] - finish |  subject to:
#    x[1] = start
#    x[n] <= finish
# This routine CAN FAIL if (finish - start)/minStep >= numPts
#
def uascanFindFactor(start center finish numPts exponent minStep) '{
  local factor fStep result f2 r2 i

  factor = 0
  result = uascanTestSeries(start, finish, numPts, factor, center, exponent, minStep)
  if (result > 0) {
    printf ("With factor=%g, could not get correct result (%g)\n", factor, result)
    #
    # fail gracefully with factor
    # let calling routine decide what to do
    # (usually just step with factor = 0 until x[i] > finish)
    #
    return (factor)
  }
  #
  # Initially, choose factor = abs(finish - start) / (numPts - 1)
  # call uascanTestSeries with factor
  #  if result<0, then factor *= 10 and repeat
  # then continue as below
  #
#  r2 = -1
#  fStep = abs(finish-start) / (numPts -1)
#  while (r2 < 0) {
#    f2 = factor + fStep
#    r2 = uascanTestSeries(start, center, finish, numPts, f2, exponent, minStep)
#    if (uascanStepDebug >= 1)
#      printf("factor = %g  result = %g\n", f2, r2)
#    if (r2 < 0) fStep *= 10
#  }
  fStep = 10
  #
  # 40 times means better than 12-digit precision
  #
  for (i = 1; i < 40; i++) {
    f2 = factor + fStep
    r2 = uascanTestSeries(start, center, finish, numPts, f2, exponent, minStep)
    if ( (r2 <= 0) && ( fabs(r2) < fabs(result) ) ) {
      factor = f2
      result = r2
    } else {
      fStep *= 0.5
    }
    if (uascanStepDebug >= 1)
      printf ("%d: f=%0.15g  result=%0.15g\n", i, factor, result)
    if ( fabs(result) < 0.5*fabs(minStep) ) break
  }
  return (factor)
}'

def _usaxs_triangulate (rot,center,dist) '{
  local offset
  offset = dist * tan((rot-center)*PI/180)
  return(offset)
}'




#global     _n1     # number of intervals
#global     _nm     # number of motors
#global     _m[]    # motor number
#global     _s[]    # start position
#global     _f[]    # finish position
#global     _d[]    # scale factor
#global     _c[]    # center position
#global     _ms[]   # minimum step size
#global     _dy0    # photodiode Y position at center angle of scan
#global     _ay0    # analyzer stage Y position at center angle of scan
#global     _exp    # exponent for step function
#global     _dir[]  # direction for motor to move
#global     _pos[]  # present function (while step scanning)
'''
    