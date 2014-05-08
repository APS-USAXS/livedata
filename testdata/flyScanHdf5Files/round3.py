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
import ustep                #@UnusedImport


MCA_CLOCK_FREQUENCY = 50e6
FIXED_VF_GAIN = 1e5   # FIXME: there is a better way to do this!  localConfig.FIXED_VF_GAIN
Q_MIN = 1.01e-6             # absolute minimum Q for rebinning
UATERM = 1.2

# TODO: need to decide how archived/reduced data files are arranged in directories
# copy code from reduceFlyData


class UsaxsFlyScan(object):
    
    def __init__(self, hdf5_file_name):
        if not os.path.exists(hdf5_file_name):
            raise IOError, 'file not found: ' + hdf5_file_name

        self.units = dict(
            ar = 'degrees',
            upd_ranges = '',
            qVec = '1/A',
            rVec = 'none',
            drVec = 'none', 
            rVec_max = 'none',
            centroid = 'degrees',
            fwhm = 'degrees',
        )
        self.min_step_factor = 1.5
        self.uaterm = UATERM

        self.hdf5_file_name = hdf5_file_name
        self.reduced = self.read_reduced()
        if 'full' not in self.reduced:
            self.reduce()
        
    def reduce(self):
        '''convert raw Fly Scan data to R(Q), also get other terms'''
        if not os.path.exists(self.hdf5_file_name):
            raise IOError, 'file not found: ' + self.hdf5_file_name
        hdf = h5py.File(self.hdf5_file_name, 'r')
    
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
        d2r = math.pi / 180
        qVec = (4*math.pi/wavelength) * numpy.sin(d2r*(ar_center - raw_ar)/2.0)

        V_f_gain = FIXED_VF_GAIN
        pulse_frequency = raw['mca_clock_frequency'][0] or  MCA_CLOCK_FREQUENCY
        channel_time_s = raw_clock_pulses / pulse_frequency
        
        amp_name = self.get_USAXS_PD_amplifier_name(hdf)
        upd_ranges = self.get_ranges(hdf, amp_name)
        upd_ranges = self.apply_upd_range_change_time_mask(hdf, upd_ranges, channel_time_s)
        gains = self.get_gain(hdf, amp_name)
        bkg   = self.get_bkg(hdf, amp_name)
        
        upd_gain = numpy.array([0,] + gains)[upd_ranges.data+1]
        upd_gain = numpy.ma.masked_less_equal(upd_gain, 0)
        upd_dark = numpy.array([0,] + bkg)[upd_ranges.data+1]
        upd_dark = numpy.ma.masked_less_equal(upd_dark, 0)
        rVec = (raw_upd - channel_time_s*upd_dark) / upd_gain / raw_I0 / V_f_gain
        
        centroid, sigma = self.mean_sigma(raw_ar, rVec)
        fwhm = sigma * 2 * math.sqrt(2*math.log(2.0))
    
        hdf.close()
        
        full = dict(
            ar = self.remove_masked_data(raw_ar, rVec.mask),
            #upd_ranges = self.remove_masked_data(upd_ranges, rVec.mask),
            qVec = self.remove_masked_data(qVec, rVec.mask),
            rVec = self.remove_masked_data(rVec, rVec.mask),
            rVec_max = rVec.max(),
            centroid = centroid,
            fwhm = fwhm,
        )
        self.reduced = dict(full = full)

    def rebin(self, bin_count = None):
        '''generate R(Q) with a bin_count bins, save in ``self.reduced[str(bin_count)]`` dict'''

        def subarray(arr, key_arr, lo, hi):
            '''return subarray of arr where lo < arr <= hi'''
            low_pass  = numpy.where(key_arr <= hi, arr,      0)
            high_pass = numpy.where(lo < key_arr,  low_pass, 0)
            return numpy.trim_zeros(high_pass)

        bin_count = bin_count or self.bin_count
        s = str(bin_count)
        if s in self.reduced:
            return self.reduced[s]
        
        qVec_full = self.reduced['full']['qVec']
        rVec_full = self.reduced['full']['rVec']
        
        # lowest non-zero Q value > 0 or minimum acceptable Q
        Qmin = max(Q_MIN, qVec_full[numpy.where(qVec_full > 0)].min() )
        Qmax = qVec_full.max()
        
        # pick smallest Q step size from input data, scale by a factor
        minStep = self.min_step_factor * numpy.min(qVec_full[1:] - qVec_full[:-1])
        # compute upper edges of bins from ustep
        qHiEdge = numpy.array(ustep.ustep(Qmin, 0.0, Qmax, bin_count, self.uaterm, minStep).series)
        # compute lower edges of bins from previous bin upper edge
        qLoEdge = numpy.insert(qHiEdge[0:-1], 0, 0.0)
        
        qVec, rVec, drVec = [], [], []
        for qLo, qHi in numpy.nditer([qLoEdge, qHiEdge]): # TODO: optimize for speed!
            q = subarray(qVec_full, qVec_full, qLo, qHi)  # all Q where qLo < Q <= qHi
            r = subarray(rVec_full, qVec_full, qLo, qHi)  # corresponding R
            
            qVec.append(  numpy.exp(numpy.mean(numpy.log(q))) ) 
            rVec.append(  numpy.exp(numpy.mean(numpy.log(r))) )
            drVec.append( r.std() )

        reduced = dict(
            qVec = numpy.array(qVec),
            rVec = numpy.array(rVec),
            drVec = numpy.array(drVec),
        )
        self.reduced[s] = reduced
        return reduced

    def read_reduced(self):
        '''
        read any and all reduced data from the HDF5 file, return in a dictionary
        
        dictionary = {
          'full': dict(qVec, rVec, rVec_max, ar, fwhm, centroid)
          '250':  dict(qVec, rVec, drVec)
          '5000': dict(qVec, rVec, drVec)
        }
        '''
        fields = self.units.keys()
        reduced = {}
        hdf = h5py.File(self.hdf5_file_name, 'r')
        entry = hdf['/entry']
        for key in entry.keys():
            if key.startswith('flyScan_reduced_'):
                nxdata = entry[key]
                nxname = key[len('flyScan_reduced_'):]
                d = {dsname: nxdata[dsname] for dsname in fields if dsname in nxdata}
                reduced[nxname] = d
        hdf.close()
        return reduced
    
    def save(self, hfile, key):
        if key not in self.reduced:
            return
        ds = self.reduced[key]
        nxname = 'flyScan_reduced_' + key
        hdf = h5py.File(hfile, 'a')
        nxentry = eznx.openGroup(hdf, 'entry', 'NXentry')
        nxdata = eznx.openGroup(nxentry, nxname, 'NXdata')
        for key in sorted(ds.keys()):
            eznx.write_dataset(nxdata, key, ds[key], units=self.units[key])
        hdf.close()

    def get_USAXS_PD_amplifier_name(self, hdf):
        base = '/entry/flyScan/upd_flyScan_amplifier'
        amp_index = hdf[base][0]
        labels = {0: base+'_ZNAM', 1: base+'_ONAM'}
        return str(hdf[labels[amp_index]][0])

    def get_ranges(self, hdf, identifier):
        '''
        return a numpy masked array of detector range changes
        
        mask is applied during a range change when requested != actual
        mask is applied for first and last point
        
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
    
    def apply_upd_range_change_time_mask(self, hdf, upd_ranges, channel_time_s):
        '''
        apply mask for specified time after a range change
        
        :param obj hdf: open FlyScan data file (h5py File object)
        :param obj upd_ranges: photodiode amplifier range (numpy masked ndarray)
        :param obj channel_time_s: measurement time in each channel, s (numpy ndarray)
        '''
        def get_mask_time_spec(r):
            # /entry/metadata/upd_amp_change_mask_time4
            return float(hdf['/entry/metadata/upd_amp_change_mask_time' + str(r)][0])
        mask_times = map(get_mask_time_spec, range(5))
        
        # modify the masks on upd_ranges
        last_range = 0
        timer = 0
        for i, upd_range in enumerate(upd_ranges.data): # TODO: optimize for speed!
            if last_range != upd_range:
                if upd_range >= 0:
                    timer = mask_times[upd_range]
            if timer > 0:
                upd_ranges[i] = numpy.ma.masked         # mask this point
                timer = max(0, timer - channel_time_s[i]) # decrement the time of this channel
            last_range = upd_range
        return upd_ranges
    
    def mean_sigma(self, x, w):
        '''
        return mean and standard deviation of weighted x array
        
        :param numpy.array x: array to be averaged
        :param numpy.array w: array of weights
        '''
        xw = x * w
        sumX = numpy.sum(xw)
        sumXX = numpy.sum(xw * xw)
        sumWt = numpy.sum(w)
        centroid = sumX / sumWt
        try:
            sigma = math.sqrt( (sumXX - (sumX*sumX)/sumWt) / (sumWt - 1) )
        except:
            sigma = 0.0
        return centroid, sigma
    
    def remove_masked_data(self, data, mask):
        '''remove all masked data'''
        arr = numpy.ma.masked_array(data=data, mask=mask)
        return arr.compressed()


def main(hfile):
    ufs = UsaxsFlyScan(hfile)
    #ufs.reduce()
    ufs.save('reduced.h5', 'full')
    ufs.rebin(250)
    ufs.save('reduced.h5', str(250))


if __name__ == '__main__':
    main('S563_PB_GRI_9_Nat_200C.h5')
    #main('S555_PB_GRI_9_Nat_175C.h5')
    #main('S571_Heater_Blank.h5')


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
