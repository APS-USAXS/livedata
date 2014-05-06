'''
third try to get the FlyScan data reduction right
'''

import os                   #@UnusedImport
import glob                 #@UnusedImport
from spec2nexus import eznx
import numpy                #@UnusedImport
import h5py                 #@UnusedImport
import math                 #@UnusedImport
import datetime             #@UnusedImport


MCA_CLOCK_FREQUENCY = 50e6
FIXED_VF_GAIN = 1e5   # FIXME: not the correct way to do this!  localConfig.FIXED_VF_GAIN


# TODO: need to decide how archived/reduced data files are arranged in directories


class UsaxsFlyScan(object):
    
    def __init__(self, hdf5_file_name):
        if not os.path.exists(hdf5_file_name):
            raise IOError, 'file not found: ' + hdf5_file_name
        self.hdf5_file_name = hdf5_file_name
        self.reduced = self.read_reduced()
        if 'full' not in self.reduced:
            self.reduce()
        
    def reduce(self):
        '''convert raw Fly Scan data to R(Q), also get other terms'''
        if not os.path.exists(self.hdf5_file_name):
            raise IOError, 'file not found: ' + self.hdf5_file_name
        hdf = h5py.File(self.hdf5_file_name, 'r')
    
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
        
        amp_name = self.get_USAXS_PD_amplifier_name(hdf)
        upd_ranges = self.get_ranges(hdf, amp_name)
        V_f_gain = FIXED_VF_GAIN
        gains = self.get_gain(hdf, amp_name)
        bkg   = self.get_bkg(hdf, amp_name)
        
        upd_gain = numpy.array([0,] + gains)[upd_ranges.data+1]
        upd_gain = numpy.ma.masked_less_equal(upd_gain, 0)
        upd_dark = numpy.array([0,] + bkg)[upd_ranges.data+1]
        upd_dark = numpy.ma.masked_less_equal(upd_dark, 0)
        pulse_frequency = raw['mca_clock_frequency'][0] or  MCA_CLOCK_FREQUENCY
        channel_time_s = raw_clock_pulses / pulse_frequency
        rVec = (raw_upd - channel_time_s*upd_dark) / upd_gain / raw_I0 / V_f_gain
        centroid = numpy.sum(rVec*raw_ar) / numpy.sum(rVec)
        
        fwhm = 0.0        # TODO: compute FWHM
    
        hdf.close()
        
        full = dict(
            ar = raw_ar,
            upd_ranges = upd_ranges,
            qVec = qVec,
            rVec = rVec,
            centroid = centroid,
            fwhm = fwhm,
        )
        self.reduced = dict(full = full)

    def read_reduced(self):
        '''
        read any and all reduced data from the HDF5 file, return in a dictionary
        
        dictionary = {
          'full': dict(Q, R, R_max, AR, AR_FWHM, AR_centroid)
          '250':  dict(Q, R, dR)
          '5000': dict(Q, R, dR)
        }
        '''
        fields = ('Q', 'R', 'dR', 'R_max', 'AR', 'AR_centroid', 'AR_FWHM')
        reduced = {}
        hdf = h5py.File(self.hdf5_file_name, 'r')
        entry = hdf['/entry']
        for key in entry.keys():
            if key.startswith('flyScan_reduced_'):
                nxdata = entry[key]
                reduction_name = key[len('flyScan_reduced_'):]
                # extract the Numpy structure!
                d = {dsname: nxdata[dsname] for dsname in fields if dsname in nxdata}
                reduced[reduction_name] = d
        hdf.close()
        return reduced

    def get_USAXS_PD_amplifier_name(self, hdf):
        base = '/entry/flyScan/upd_flyScan_amplifier'
        amp_index = hdf[base][0]
        labels = {0: base+'_ZNAM', 1: base+'_ONAM'}
        return str(hdf[labels[amp_index]][0])

    def get_ranges(self, hdf, identifier):
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

    def get_gain(self, hdf, amplifier):
        '''
        get gains for named amplifier from the HDF5 file
        
        :param obj hdf: opened HDF5 file instance
        :param str amplifier: amplifier name, as stored in the HDF5 file
        '''
        # TODO: consider the numpy array.where() method with a ranges array with just the changes
        def load_gain(x):
            return hdf[base+str(x)][0]
        base = '/entry/metadata/' + amplifier + '_gain'
    #     gain = [hdf[base+str(_)][0] for _ in range(5)]
        gain = map(load_gain, range(5))
        return gain
    
    
    def get_bkg(self, hdf, amplifier):
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


def main(hfile):
    ufs = UsaxsFlyScan(hfile)
    full = ufs.reduced['full']

    hdf = h5py.File('reduced.h5', 'w')
    nxentry = eznx.openGroup(hdf, 'entry', 'NXentry')
    nxdata = eznx.openGroup(nxentry, 'reduced', 'NXdata')
    eznx.write_dataset(nxdata, 'ar',            full['ar'],         units='degrees')
    eznx.write_dataset(nxdata, 'upd_ranges',    full['upd_ranges'], units='masked')
    eznx.write_dataset(nxdata, 'qVec',          full['qVec'],       units='1/A')
    eznx.write_dataset(nxdata, 'rVec',          full['rVec'],       units='none')
    eznx.write_dataset(nxdata, 'centroid',      full['centroid'],   units='degrees')
    hdf.close()


if __name__ == '__main__':
    main('S563_PB_GRI_9_Nat_200C.h5')
