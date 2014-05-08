#!/usr/bin/env python

'''
Step-Size Algorithm for Bonse-Hart Ultra-Small-Angle Scattering Instruments

:see: http://usaxs.xray.aps.anl.gov/docs/ustep/index.html
'''


class ustep(object):
    '''
    find the series of positions for the USAXS

    :param float start: required first position of list
    :param float center: position to take minStep
    :param float finish: required ending position of list
    :param float numPts: length of the list
    :param float exponent: :math:`\eta`, exponential factor
    :param float minStep: smallest allowed step size
    :param float factor: :math:`k`, multiplying factor (computed internally)
    :param [float] series: computed list of positions
    '''
    
    def __init__(self, start, center, finish, numPts, exponent, minStep):
        self.start = start
        self.center = center
        self.finish = finish
        self.numPts = numPts
        self.exponent = exponent
        self.minStep = minStep
        self.sign = {True: 1, False: -1}[start < finish]
        self.series = []
        self.factor = self.find_factor()
        
    def find_factor(self):
        '''
        Determine the factor that will make a series with the specified parameters.
        
        This method improves on find_factor_simplistic() by choosing next 
        choice for factor from recent history.
        '''
        
        def assess(factor):
            self.make_series(factor)
            span_diff = abs(self.series[0] - self.series[-1]) - span_target
            return span_diff
            
        span_target = abs(self.finish - self.start)
        span_precision = abs(self.minStep) * 0.2
        factor = abs(self.finish-self.start) / (self.numPts -1)
        span_diff = assess(factor)
        fLo, fHi = factor, factor
        dLo, dHi = span_diff, span_diff
        
        # first make certain that dLo < 0 and dHi > 0, expand fLo and fHi
        for _ in range(100):
            if dLo * dHi < 0:
                break           # now, dLo and dHi have opposite sign
            if span_diff < 0:
                factor *= 2
            else:
                factor /= 2
            span_diff = assess(factor)
            if span_diff > dHi:
                fHi = factor
                dHi = span_diff
            if span_diff < dLo:
                fLo = factor
                dLo = span_diff
        
        # now: dLo < 0 and dHi > 0
        for _ in range(100):
            if (dHi - dLo) > span_target:
                factor = (fLo + fHi)/2              # bracket by bisection when not close
            else:
                factor = fLo - dLo * (fHi-fLo)/(dHi-dLo)    # linear interpolation when close
            span_diff = assess(factor)
            if abs(span_diff) <= span_precision:
                break
            if span_diff < 0:
                fLo = factor
                dLo = span_diff
            else:
                fHi = factor
                dHi = span_diff

        return factor
        
    def find_factor_simplistic(self):
        '''
        Determine the factor that will make a series with the specified parameters.
        
        Choose the factor that will minimize :math:`| x_n - finish |` subject to:
        
        .. math::
        
           x_1 = start
           x_n <= finish
        
        This routine CAN FAIL if :math:`(finish - start)/minStep >= numPts`
        
        This search technique picks a new factor based on the fit of the present choice.
        It converges but not quickly.
        '''
        #print '\t'.join('factor diff'.split())
        span_target = abs(self.finish - self.start)
        span_precision = abs(self.minStep) * 0.2
        factor = abs(self.finish-self.start) / (self.numPts -1)
        fStep = factor
        larger = 3.0
        smaller = 0.5
        f, d = [], []
        for _ in range(100):
            self.make_series(factor)
            span = abs(self.series[0] - self.series[-1])
            span_diff = span - span_target
            #print '\t'.join(map(str,[factor, span_diff]))
            if abs(span_diff) <= span_precision:
                break
            if span_diff < 0:
                fStep = abs(fStep) * larger
            else:
                fStep = -abs(fStep) * smaller
            factor += fStep
        return factor
    
    def make_series(self, factor):
        '''create self.series with the given factor'''
        x = self.start
        series = [x, ]
        for _ in range(self.numPts - 1):
            x += self.sign * self.uascanStepFunc(x, factor)
            series.append(x)
        self.series = series
    
    def uascanStepFunc(self, x, factor):
        '''Calculate the next step size with the given parameters'''
        if abs(x - self.center) > 1e100:
            step = 1e100
        else:
            step = factor * pow( abs(x - self.center), self.exponent ) + self.minStep
        return step


def main():
    start = 10.0
    center = 9.5
    finish = 7
    numPts = 100
    exponent = 1.2
    minStep = 0.0001
    u = ustep(start, center, finish, numPts, exponent, minStep)
    print u.factor
    print u.series


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
