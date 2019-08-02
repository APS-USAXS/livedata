
"""
compute centroid of USAXS fly scan data
"""

import h5py
import numpy
import os
import sys

import reduceFlyData
import calc

path = os.path.dirname(__file__)
TESTFILE = os.path.join(path, "testdata", "Blank_0016.h5")
OUTFILE = os.path.join(path, "testdata", "Blank_0016_center_calc.h5")


def centroid(x, y):
    '''compute centroid of y(x)'''
    import scipy.integrate
    weight = y*y
    top    = scipy.integrate.simps(x*weight, x)
    bottom = scipy.integrate.simps(weight, x)
    center = top/bottom
    return center


def flyscan_centroid(x, y, peak_index, cutoff):
    # walk down each side from the peak
    n = len(x)

    pLo = peak_index
    while pLo >= 0 and y[pLo] > cutoff:
        pLo -= 1

    pHi = peak_index + 1
    while pHi < n and y[pHi] > cutoff:
        pHi += 1
    
    print pLo, pHi
    ar = x[pLo:pHi]
    R = y[pLo:pHi]

    cen = centroid(ar, R)
    return cen, ar, R

    
def main():
    fly = reduceFlyData.UsaxsFlyScan(TESTFILE)
    fly.reduce()
    full = fly.reduced["full"]

    print full.keys()
    print "ar[:5]", full['ar'][:5]
    for k in "R_max r_peak ar_r_peak".split():
        print k, full[k]
    
    peak_index = numpy.where(full["ar"]==full["ar_r_peak"])[0][0]
    print "peak index:", peak_index
    
    cen, ar, R = flyscan_centroid(
        full["ar"],
        full["R"],
        peak_index,
        full["R_max"] * 0.4,
    )
    print "centroid:", cen
    
    with h5py.File(OUTFILE, "w") as h5:
        h5.create_dataset("ar", data=ar)
        h5.create_dataset("R", data=R)
        h5.create_dataset("cen", data=cen)


if __name__ == "__main__":
    main()
