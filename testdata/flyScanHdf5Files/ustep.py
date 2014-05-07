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
########### SVN repository information ###################
# :HeadURL: https://subversion.xray.aps.anl.gov/spec/beamline_config/trunk/usaxs/usaxs/usaxs_uascan.mac
########### SVN repository information ###################

# these are now epics variables
#global     AR_VAL_CENTER                 # center value for AR stage
#global     NUMPTS                        # number of points
#global     UATERM                        # exponent... Changes spread of the log stepping
#global     START_OFFSET                  # Q offset to start above AR_VAL_CENTER
#global     FINISH                        # end angle for USAXS scans
#global     USAXS_MINSTEP                 # min step of uascan
#

###################################################################################
####
####  general scan macro for USAXS for both 1D & 2D collimations
####
def USAXSscan '{
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

  uascan ar START AR_VAL_CENTER Finish_in_Angle MINSTEP DY0 SDD AY0 SAD UATERM NUMPNTS TIME

'

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


    # find appropriate factor for weighing the points
    k = uascanFindFactor(start, center, finish, intervals, exponent, minStep)
    # ...
    _pos = start
    
    # ...
    _pos += _dir * uascanStepFunc(_pos, k, center, exponent, minStep)
    # ...
'

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
