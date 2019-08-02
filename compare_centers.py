
"""
compute centroid of USAXS fly scan data
"""

import h5py
import numpy
import os

import reduceFlyData


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


def flyscan_centroid(dataset, cutoff_fraction):
    """
    compute the center of the fly scan from data near the peak
    
    PARAMETERS
    
    dataset : dict
        A dictionary as received from the `reduceFlyData()` object.
        Contains reduced USAXS data.  
        
        Expect to find these keys in *dataset*:
        
        * ar : numpy array of angles
        * R: numpy array of reduced intensities
        * R_max: maximum value of *R*
        * ar_r_peak: value of *ar* at *R_max*

    cutoff_fraction : float
        Discard any data with R < cutoff_fraction * max(R)
    
    RETURNS
    
    tuple
        (center, ar, R): 
        
        * center: computed centroid
        * ar: (numpy) array of the *ar* axis near the peak center
        * R: (numpy) array of the *R* axis near the peak center
    
    """
    x = dataset["ar"]
    y = dataset["R"]
    peak_index = numpy.where(x==dataset["ar_r_peak"])[0][0]
    cutoff = dataset["R_max"] * cutoff_fraction

    print "peak index:", peak_index

    # walk down each side from the peak
    n = len(x)

    pLo = peak_index
    while pLo >= 0 and y[pLo] > cutoff:
        pLo -= 1

    pHi = peak_index + 1
    while pHi < n and y[pHi] > cutoff:
        pHi += 1

    # enforce boundaries
    pLo = max(0, pLo+1)
    pHi = min(n-1, pHi-1)
    
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
    
    cen, ar, R = flyscan_centroid(full, 0.4)
    print "centroid:", cen
    
    with h5py.File(OUTFILE, "w") as h5:
        h5.attrs["default"] = "entry"
        nxentry = h5.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"
        nxentry.attrs["default"] = "data"
        nxdata = nxentry.create_group("data")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "R"
        nxdata.attrs["axes"] = "ar"
        ds = nxdata.create_dataset("ar", data=ar)
        ds.attrs["units"] = "degrees"
        ds = nxdata.create_dataset("R", data=R)
        ds.attrs["units"] = "not applicable"
        ds = nxdata.create_dataset("cen", data=[cen])
        ds.attrs["units"] = "degrees"


if __name__ == "__main__":
    main()
