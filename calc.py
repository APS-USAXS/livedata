#!/usr/bin/env python

'''
Calculate R(Q) from arrays of measured data using numpy
'''


import h5py
import math
import numpy
import os

import spec2nexus.spec


TEST_FILE_FLYSCAN = os.path.join('testdata', 'S217_E7_600C_87min.h5')
TEST_FILE_UASCAN = os.path.join('testdata', '03_18_GlassyCarbon.dat')
TEST_UASCAN_SCAN_NUMBER = 522


class FileNotFound(RuntimeError): pass


class Scan(object):
    '''representation of a USAXS scan'''
    
    file = None
    number = -1
    title = ''
    started = ''
    specscan = None
    qVec = []
    rVec = []


def calc_R_Q(wavelength, ar, seconds, pd, pd_bkg, pd_gain, I0, I0_bkg=None, I0_gain=None, ar_center=None, V_f_gain=None):
    '''
    Calculate :math:`R(Q)`
    
    :param float wavelength: :math:`lambda`, (:math:`\A`)
    :param float ar_center: center of rocking curve along AR axis
    :param numpy.ndarray([float]) ar: array of crystal analyzer angles
    :param numpy.ndarray([float]) seconds: array of counting time for each point
    :param numpy.ndarray([float]) pd: array of photodiode counts
    :param numpy.ndarray([float]) pd_bkg: array of photodiode amplifier backgrounds
    :param numpy.ndarray([float]) pd_gain: array of photodiode amplifier gains
    :param numpy.ndarray([float]) I0: array of incident monitor counts
    :param numpy.ndarray([float]) I0_bkg: array of I0 backgrounds
    :param numpy.ndarray([float]) I0_gain: array of I0 gains
    :param numpy.ndarray([float]) V_f_gain: array of voltage-frequency converter gains
    :returns dictionary: Q, R
    :param numpy.ndarray([float]) qVec: :math:`Q`
    :param numpy.ndarray([float]) rVec: :math:`R = I/I_o`
    '''

    def amplifier_corrections(signal, dark, gain):
        #v = (signal - seconds*dark) / gain
        v = numpy.array(signal)
        if dark is not None:      # compatibility with older USAXS data
            v -= seconds*dark
        if gain is not None:     # compatibility with older USAXS data
            v /= gain
        return v

    r  = amplifier_corrections(pd, pd_bkg, pd_gain)
    r0 = amplifier_corrections(I0, I0_bkg, I0_gain)
    
    rVec = r / r0
    if V_f_gain is not None:        # but why?
        rVec /= V_f_gain
    rVec = numpy.ma.masked_less_equal(rVec, 0)
    
    if ar_center is None:       # compute ar_center from rVec and ar
        ar_center = ar[0]       # first ar value
        ar_center = ar[numpy.argmax(rVec)]  # ar value of peak R
        # TODO: centroid of central peak

    d2r = math.pi / 180
    qVec = (4 * math.pi / wavelength) * numpy.sin(d2r*(ar_center - ar)/2)
    
    result = dict(Q=qVec, R=rVec, r=r, r0=r0, ar_0=ar_center)
    return result


def test_flyScan(filename):
    '''test data reduction from a flyScan (in an HDF5 file)'''
    if not os.path.exists(filename):
        raise FileNotFound(filename)
    
    # open the HDF5 data file
    hdf = h5py.File(filename, 'r')
    metadata = hdf['/entry/metadata']
    flyScan  = hdf['entry/flyScan']

    # get the raw data from the data file
    wavelength = hdf['/entry/instrument/monochromator/wavelength'][0]
    ar_center  = float(hdf['/entry/metadata/AR_center'][0])

    raw_clock_pulses =  flyScan['mca1']
    raw_I0 =            flyScan['mca2']
    raw_upd =           flyScan['mca3']

    raw_num_points =    int(flyScan['AR_pulses'][0])
    AR_start =          float(flyScan['AR_start'][0])
    AR_increment =      float(flyScan['AR_increment'][0])

    # mbbi PV should return strings but instead returns index number
    # these are the values and a cross-reference to the name strings
    AR_MODE_FIXED = 0       # fixed pulses (version 1)
    AR_MODE_ARRAY = 1       # use PulsePositions
    AR_MODE_TRAJECTORY = 2  # use trajectory points (a.k.a. waypoints)
    MODENAME_XREF = {     # these are the strings the PV *should* return
                 AR_MODE_FIXED:         'Fixed',
                 AR_MODE_ARRAY:         'Array',
                 AR_MODE_TRAJECTORY:    'TrajPts',
                 }

    # compute the angle and intensity data from the MCA waveforms
#     ar               = numpy.array(sds.data['ar'])
#     seconds          = numpy.array(sds.data['seconds'])
#     pd               = numpy.array(sds.data['pd_counts'], dtype=int)
#     I0               = numpy.array(sds.data['I0'], dtype=int)
#     I0_constant_gain = numpy.array(sds.metadata['I0AmpGain'])
#     pd_range         = numpy.array(sds.data['pd_range'], dtype=int)

#     # gain & dark are stored as 1-offset, pad here with 0-offset to simplify list handling
#     gain = [0, ] + map(lambda _: sds.metadata["UPD2gain" + str(_)], range(1,6))
#     dark = [0, ] + map(lambda _: sds.metadata["UPD2bkg" + str(_)], range(1,6))

    hdf.close()
 
    # create numpy arrays to match the ar & pd data
    pd_gain = map(lambda _: gain[_], pd_range)
    pd_dark = map(lambda _: dark[_], pd_range)

    # compute the R(Q) profile
    usaxs = calc_R_Q(wavelength, ar, seconds, pd, pd_dark, pd_gain, I0)
    return usaxs


def test_uascan(filename):
    '''test data reduction from an uascan (in a SPEC file)'''
    if not os.path.exists(filename):
        raise FileNotFound(filename)

    # open the SPEC data file
    sdf_object = spec2nexus.spec.SpecDataFile(filename)
    sds = sdf_object.getScan(TEST_UASCAN_SCAN_NUMBER)
    sds.interpret()

    # get the raw data from the data file
    wavelength       = float(sds.metadata['DCM_lambda'])
    ar               = numpy.array(sds.data['ar'])
    seconds          = numpy.array(sds.data['seconds'])
    pd               = numpy.array(sds.data['pd_counts'], dtype=int)
    I0               = numpy.array(sds.data['I0'], dtype=int)
    I0_constant_gain = numpy.array(sds.metadata['I0AmpGain'])
    pd_range         = numpy.array(sds.data['pd_range'], dtype=int)

    # gain & dark are stored as 1-offset, pad here with 0-offset to simplify list handling
    gain = [0, ] + map(lambda _: sds.metadata["UPD2gain" + str(_)], range(1,6))
    dark = [0, ] + map(lambda _: sds.metadata["UPD2bkg" + str(_)], range(1,6))

    # create numpy arrays to match the ar & pd data
    pd_gain = map(lambda _: gain[_], pd_range)
    pd_dark = map(lambda _: dark[_], pd_range)

    # compute the R(Q) profile
    usaxs = calc_R_Q(wavelength, ar, seconds, pd, pd_dark, pd_gain, I0)
    return usaxs


def developer_main():
    path = os.path.dirname(__file__)
#     hdf5FileName = os.path.abspath(os.path.join(path, TEST_FILE_FLYSCAN))
#     test_flyScan(hdf5FileName)
    
    specFileName = os.path.abspath(os.path.join(path, TEST_FILE_UASCAN))
    test_uascan(specFileName)


if __name__ == '__main__':
    developer_main()
