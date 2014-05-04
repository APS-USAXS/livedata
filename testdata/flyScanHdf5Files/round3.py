'''
third try to get the FlyScan data reduction right
'''

import os                   #@UnusedImport
import glob                 #@UnusedImport
import spec2nexus           #@UnusedImport
import numpy                #@UnusedImport
import h5py                 #@UnusedImport
import math                 #@UnusedImport
import datetime             #@UnusedImport


def get_USAXS_PD_amplifier_name(hdf):
    base = '/entry/flyScan/upd_flyScan_amplifier'
    amp_index = hdf[base][0]
    labels = {0: base+'_ZNAM', 1: base+'_ONAM'}
    return str(hdf[labels[amp_index]][0])


def get_gain(hdf, amplifier):
    '''
    get gains for named amplifier from the HDF5 file
    
    :param obj hdf: opened HDF5 file instance
    :param str amplifier: amplifier name, as stored in the HDF5 file
    '''
    def load_gain(x):
        return hdf[base+str(x)][0]
    base = '/entry/metadata/' + amplifier + '_gain'
#     gain = [hdf[base+str(_)][0] for _ in range(5)]
    gain = map(load_gain, range(5))
    return gain


def get_bkg(hdf, amplifier):
    '''
    get backgrounds for named amplifier from the HDF5 file
    
    :param obj hdf: opened HDF5 file instance
    :param str amplifier: amplifier name, as stored in the HDF5 file
    '''
    def load_bkg(x):
        return hdf[base+str(x)][0]
    base = '/entry/metadata/' + amplifier + '_bkg'
    bkg = map(load_bkg, range(5))
    return bkg


def get_ranges(hdf, identifier):
    '''
    return a numpy masked array of detector range changes
    
    mask_value is true during a range change when requested != actual
    mask_value is true for first and last point
    
    :param obj hdf: opened HDF5 file instance
    :param str identifier: amplifier name, as stored in the HDF5 file
    '''

    def assign_range_value(start, end, range_value):
        '''short-hand assignment'''
        if end - start >= 0:    # define the valid range
            ranges[start:end] = numpy.zeros((end - start,)) + range_value

    num_channels = hdf['/entry/flyScan/AR_pulses'][0]
    base = '/entry/flyScan/changes_' + identifier + '_'
    arr_channel   = hdf[base + 'mcsChan']
    arr_requested = hdf[base + 'ampReqGain']
    arr_actual    = hdf[base + 'ampGain']

    ranges = numpy.arange(int(num_channels))
    mask_value = -1
    last = None
    for key, chan  in enumerate(arr_channel):
        requested = arr_requested[key]
        actual = arr_actual[key]
        if last is not None:
            if requested == actual:     # mark a range change as invalid
                assign_range_value(last['chan'], chan, mask_value)
            else:                       # mark the range for these channels
                assign_range_value(last['chan']+1, chan, last['actual'])
        ranges[chan] = mask_value
        last = dict(chan=chan, requested=requested, actual=actual)
        if chan == arr_channel.value.max():               # end of Fly Scan range change data
            break

    if last is not None:                # mark the final range
        assign_range_value(last['chan']+1, num_channels, last['actual'])

    ranges[-1] = mask_value             # assume this, for good measure
    return numpy.ma.masked_less_equal(ranges, mask_value)


def main():
    hdf = h5py.File('S563_PB_GRI_9_Nat_200C.h5', 'r')

    MCA_CLOCK_FREQUENCY = 50e6
    d2r = math.pi / 180
    wavelength = float(hdf['/entry/instrument/monochromator/wavelength'][0])
    ar_center  = float(hdf['/entry/metadata/AR_center'][0])

    raw = hdf['entry/flyScan']

    raw_clock_pulses =  raw['mca1']
    raw_I0 =            raw['mca2']
    raw_upd =           raw['mca3']

    raw_num_points =    int(raw['AR_pulses'][0])
    AR_start =          float(raw['AR_start'][0])
    AR_increment =      float(raw['AR_increment'][0])
    raw_ar = AR_start - numpy.arange(raw_num_points) * AR_increment
    qVec = (4*math.pi/wavelength) * numpy.sin(d2r*(ar_center - raw_ar)/2.0)
    
    amp_name = get_USAXS_PD_amplifier_name(hdf)
    upd_ranges = get_ranges(hdf, amp_name)
    V_f_gain = 1e5   # FIXME: not the correct number!  localConfig.FIXED_VF_GAIN
    gains = get_gain(hdf, amp_name)
    bkg   = get_bkg(hdf, amp_name)
    
    upd_gain = numpy.array([0,] + gains)[upd_ranges.data+1]
    upd_gain = numpy.ma.masked_less_equal(upd_gain, 0)
    upd_dark = numpy.array([0,] + bkg)[upd_ranges.data+1]
    upd_dark = numpy.ma.masked_less_equal(upd_dark, 0)
    pulse_frequency = raw['mca_clock_frequency'][0] or  MCA_CLOCK_FREQUENCY
    channel_time_s = raw_clock_pulses / pulse_frequency
    rVec = (raw_upd - channel_time_s*upd_dark) / upd_gain / raw_I0 / V_f_gain
    centroid = numpy.sum(rVec*raw_ar) / numpy.sum(rVec)

    hdf.close()

    hdf = h5py.File('reduced.h5', 'w')
    from spec2nexus import eznx
    nxentry = eznx.openGroup(hdf, 'entry', 'NXentry')
    nxdata = eznx.openGroup(nxentry, 'reduced', 'NXdata')
    eznx.write_dataset(nxdata, 'ar', raw_ar, units='degrees')
    eznx.write_dataset(nxdata, 'upd_ranges', upd_ranges, units='masked')
    eznx.write_dataset(nxdata, 'qVec', qVec, units='1/A')
    eznx.write_dataset(nxdata, 'rVec', rVec, units='none')
    eznx.write_dataset(nxdata, 'centroid', centroid, units='degrees')
    hdf.close()


if __name__ == '__main__':
    main()
