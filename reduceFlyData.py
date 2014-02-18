#!/usr/bin/env python

'''reduce the fly scan data from the 2013-12-09 tests'''

# export EPD=/APSshare-ro/epd/rh6-x86_64/bin/python
# alias EPD '/APSshare-ro/epd/rh6-x86_64/bin/python '


import os
import sys
import math
import numpy
import h5py


DEFAULT_NUM_BINS = 300


def get_data(dataset, astype=None):
    '''get the numpy data from the HDF5 dataset, option to return as different numpy data type'''
    dtype = dataset.dtype
    if astype is not None:
        dtype = astype
    if len(dataset.shape) > 1:
        raise RuntimeError, "unexpected %d-D data" % len(dataset.shape)
    if dataset.size > 1:
        return dataset[...].astype(dtype)   # as array
    else:
        return dataset[0].astype(dtype)     # as scalar


class UsaxsFlyScanData(object):
    '''contains data from one HDF5 file of fly scan raw data'''

    range_adjustment_constant = 500.0     # why this number?
    pulse_frequency = 50.0e6              # 50 MHz
    
    def __init__(self, hdf_filename, bin_count=250):
        self.hdf_filename = hdf_filename
        if not os.path.exists(hdf_filename):
            raise RuntimeError, 'file not found: ' + hdf_filename
        
        self.bin_count = bin_count
        self.hdf = h5py.File(hdf_filename, "r")
        self.read_raw_data(self.hdf['/entry/flyScan'])
        self.compute_ar(self.hdf['/entry/flyScan'])
        self.basic_reduction()
        self.compute_Q_and_R()
        self.rebin(Qmax=0.25, number_bins=self.bin_count)
        #self.hdf.close()        # let the caller close the file
        
    def __str__(self):
        return self.hdf_filename
        
    def read_raw_data(self, nxdata):
        '''pull the raw data from the HDF5 file'''
        self.raw_clock_pulses = get_data(nxdata['mca1'])
        self.raw_I0 = get_data(nxdata['mca2'])
        self.raw_I0_ranges = get_data(nxdata['mca5'])
        self.raw_upd = get_data(nxdata['mca3'])
        self.raw_upd_ranges = get_data(nxdata['mca4'])
        self.raw_ay_fly_pulses = get_data(nxdata['mca6'])
        self.raw_dy_fly_pulses = get_data(nxdata['mca7'])
        self.num_points = get_data(nxdata['AR_pulses'])
        
    def compute_ar(self, nxdata):
        '''compute the AR array from available information, constant AR step size'''
        ar_start = get_data(nxdata['AR_start'])
        ar_step = get_data(nxdata['AR_increment'])
        last = ar_start - (self.num_points - 1) * ar_step
        self.ar = numpy.linspace(ar_start, last, self.num_points)

    def compute_range_change_mask(self):
        '''
        mask any channels associated with a range change
        
        note: In NumPy, masks are True to ignore the datum, 
              False if the datum is good.
              Here, we compute the data_ok and then return the opposite.
        
        (0.2 s before to 0.1 after, perhaps)
        the masking time could be range-change dependent 
        (or learned from reqrange v. lurange or ...)
        '''
        # 1. determine channels with range change
        # 2. compute mask
        # 3. return the mask
        time_before = 0.2       # for starters, independent of range or range-change
        time_after = 0.3        # these values chosen by looking at 2013-12-09 data
        abs_time = numpy.cumsum(self.time)

        # Determine range changes by difference method
        # Changes occur when self.ranges[i] != shifted[i]
        old_range = numpy.insert(self.ranges, 0, -1)
        new_range = numpy.append(self.ranges, -2)
        lu_range_change_channels = numpy.nonzero(new_range - old_range)[0][1:-1]

        data_ok = numpy.ma.make_mask(self.ranges + 1) # initial mask all true
        size = abs_time.size
        for channel in lu_range_change_channels:
            data_ok[channel] = False
            t0 = abs_time[channel]
            t1 = t0 - time_before
            t2 = t0 + time_after
            
            # mask some channels just before the range change
            ch_1 = channel - 1
            while ch_1 > 0:
                if not data_ok[ch_1]:
                    break       # previously masked, no need to continue
                data_ok[ch_1] = False
                if abs_time[ch_1] < t1:
                    break       # end of masking range
                ch_1 -= 1
            
            # mask some channels just after the range change
            ch_n = channel + 1
            while ch_n < size:
                if not data_ok[ch_n]:
                    break       # previously masked, no need to continue
                data_ok[ch_n] = False
                if abs_time[ch_n] > t2:
                    break       # end of masking range
                ch_n += 1
        
        return ~data_ok
        
    def basic_reduction(self):
        '''straight USAXS data reduction to R(ar), no rebinning now'''
        numpy_error_reporting = numpy.geterr()
        numpy.seterr(divide='ignore', invalid='ignore')     # suppress messages

        # 0 means no data, >0 means valid range
        range_pulses = numpy.ma.masked_equal(self.raw_upd_ranges, 0)  
        arr = self.range_adjustment_constant * range_pulses / self.raw_clock_pulses
        ranges = numpy.ma.masked_invalid(arr)
        self.ranges = ranges.astype(int)
        
        arr = self.raw_clock_pulses / self.pulse_frequency
        self.time = numpy.ma.masked_array(data=arr, mask=ranges.mask)
        
        # get the table of amplifier gains and measured backgrounds
        meta = self.hdf['/entry/metadata']
        gains_db = [get_data(meta['upd_gain' + str(_)]) for _ in range(5)]
        bkg_db = [get_data(meta['upd_bkg' + str(_)]) for _ in range(5)]

        _gain = numpy.ndarray((self.num_points,), dtype='float')
        self.gain = numpy.ma.masked_array(data=_gain,
                                          mask=ranges.mask)
        self.bkg = self.raw_clock_pulses / self.pulse_frequency
        for i in range(self.num_points):
            if not self.gain.mask[i]:
                self.gain[i] = gains_db[ self.ranges[i] ]
                self.bkg[i] *= bkg_db[ self.ranges[i] ]

        ratio = (self.raw_upd - self.bkg) / self.raw_I0 / self.gain
        ratio = numpy.ma.masked_invalid(ratio)
        ratio = numpy.ma.masked_less_equal(ratio, 0)
        self.range_change_mask = self.compute_range_change_mask()
        the_mask = ratio.mask + self.range_change_mask
        self.ratio = numpy.ma.masked_array(data=ratio, mask=the_mask)
        # TODO: error propagation

        numpy.seterr(**numpy_error_reporting)
        
    def compute_Q_and_R(self, centroid = None):
        Qmin = 1e-6
        numpy_error_reporting = numpy.geterr()
        numpy.seterr(invalid='ignore')     # suppress messages

        if centroid is not None:
            self.ar_centroid = centroid
        else:
            # simple sum since AR are equi-spaced
            numerator = numpy.ma.masked_invalid(self.ratio*self.ar)
            denominator = numpy.ma.masked_array(data=self.ratio, 
                                                mask=numerator.mask)
            self.ar_centroid = numpy.sum(numerator) / numpy.sum(denominator)
            # TODO: compute FWHM (as 2sigma)
            # TODO: save self.Rmax=R(Q=0) and normalize data to it

        wavelength = get_data(self.hdf['/entry/instrument/monochromator/DCM_wavelength'])
        d2r = math.pi/180
        q = (4 * math.pi / wavelength) * numpy.sin(d2r*(self.ar_centroid - self.ar))
        self.Q = numpy.ma.masked_less_equal( q, Qmin)
        self.R = numpy.ma.masked_array(data=self.ratio, 
                                       mask=self.Q.mask + self.ratio.mask)
        # TODO: error propagation

        numpy.seterr(**numpy_error_reporting)

    def rebin(self, Qmin=1e-5, Qmax=1, number_bins = 2000):
        # basic rebinning strategy
        numpy_error_reporting = numpy.geterr()
        numpy.seterr(invalid='ignore')

        Qmin = max(Qmin, numpy.min(self.Q))
        Qmax = min(Qmax, numpy.max(self.Q))
        Q = numpy.exp(numpy.linspace(math.log(Qmin), math.log(Qmax), number_bins))
        R = numpy.zeros((number_bins), dtype='float')
        count = numpy.zeros((number_bins), dtype='int')

        indices = numpy.digitize(self.Q, Q)
        data_mask = self.R.mask
        for i, ch in enumerate(indices):
            if not data_mask[i] and self.R[i] != numpy.nan and 0 < ch < number_bins:
                # TODO: consider weighted averages
                R[ch] += self.R[i]
                count[ch] += 1
        R = numpy.ma.masked_less_equal(numpy.ma.masked_invalid(R / count), 0)
        # TODO: error propagation
        
        Q_bin = [Q[i]  for i, value in enumerate(R) if not R.mask[i]]
        R_bin = [value for i, value in enumerate(R) if not R.mask[i]]
        self.Q_binned = numpy.array(Q_bin)
        self.R_binned = numpy.array(R_bin)
        
        numpy.seterr(**numpy_error_reporting)

    def close_hdf_file(self):
        '''close the HDF5 data file'''
        if self.hdf is not None:
            self.hdf.close()
            self.hdf = None

    def save_results(self, nxdata):
        '''save computed results to an HDF5 file (nxdata) group'''
        import eznx
        eznx.makeDataset(nxdata, 'Q_binned', self.Q_binned, units='1/A')
        eznx.makeDataset(nxdata, 'R_binned', self.R_binned, units='a.u.',      signal=1, axes='Q_binned')
        
        other_data = eznx.makeGroup(nxdata, 'other_data', 'NXdata')

        wavelength = get_data(self.hdf['/entry/instrument/monochromator/DCM_wavelength'])
        energy = get_data(self.hdf['/entry/instrument/monochromator/DCM_energy'])
        sdd = get_data(self.hdf['/entry/metadata/detector_distance'])
        
        eznx.makeDataset(other_data, 'Q', self.Q, units='1/A')
        eznx.makeDataset(other_data, 'R', self.R, units='a.u.',      signal=1, axes='Q')
        
        eznx.makeDataset(other_data, 'ar', self.ar, units='degrees')
        eznx.makeDataset(other_data, 'ranges', self.ranges)
        eznx.makeDataset(other_data, 'bkg', self.bkg, units='counts/s')
        eznx.makeDataset(other_data, 'ratio', self.ratio, units='a.u.')
        eznx.makeDataset(other_data, 'time', self.time, units='s')
        eznx.makeDataset(other_data, 'gain', self.gain, units='V/A')
        eznx.makeDataset(other_data, 'raw_upd', self.raw_upd, units='counts')
        eznx.makeDataset(other_data, 'raw_I0', self.raw_I0, units='counts')
        eznx.makeDataset(other_data, 'raw_clock_pulses', self.raw_clock_pulses, units='counts')
        eznx.makeDataset(other_data, 'range_change_mask', self.range_change_mask)
        eznx.makeDataset(other_data, 'data_mask', self.R.mask)

        eznx.makeDataset(other_data, 'wavelength', [wavelength], units='A')
        eznx.makeDataset(other_data, 'energy', [energy], units='keV')
        eznx.makeDataset(other_data, 'SDD', [sdd], units='mm')
        eznx.makeDataset(other_data, 'ar_centroid', [self.ar_centroid], units='degrees')


def main():
    '''standard command-line interface'''
    import argparse
    import eznx
    parser = argparse.ArgumentParser(prog='reduceFlyData', 
                                     description='reduce USAXS fly scan data to R(Q)')
    parser.add_argument('infile', 
                        action='store', 
                        help="input HDF5 file name")
    parser.add_argument('outfile', 
                        action='store', 
                        help="output HDF5 file name")
    msg =  'how many bins in output R(Q)?'
    msg += '  default = %d' % DEFAULT_NUM_BINS
    parser.add_argument('-n', 
                        '--num_bins',
                        dest='num_bins',
                        type=int,
                        default=DEFAULT_NUM_BINS,
                        help=msg)
    parser.add_argument('-V', 
                        '--version', 
                        action='version', 
                        version='$Id$')

    print sys.argv
    cmd_args = parser.parse_args()

    hdf = UsaxsFlyScanData(cmd_args.infile, bin_count=cmd_args.num_bins)
    out = eznx.makeFile(cmd_args.outfile)
    entry = eznx.makeGroup(out, 'flyScan_reduced', 'NXentry')
    key = os.path.splitext(os.path.basename(cmd_args.infile))[0]
    print 'Saving NXdata group: ' + key
    data = eznx.makeGroup(entry, key, 'NXdata')
    hdf.save_results(data)
    hdf.close_hdf_file()
    out.close()


def developer_main():
    '''
    First, find the directory that exists on our computer.
    Since we develop and process on several computers, the data might
    exist on different file paths depending on the system.
    
    Next, try to load and process from all HDF5 files.  Leave the files open
    so the datasets remain accessible through the next step.  For now,
    no data rebinning is done.
    
    Once we have a list of fly scans that could be processed,
    create an HDF5/NeXus file for output of all results.

    Need to learn how to process the data when the pulse count for
    some channels is zero.  Learn how to avoid divide-by-zero errors
    in Numpy.  This will allow us to see the results from 20s fly scans.

    Place result for each fly scan in its own NXdata group under a
    single NXentry group.  (Could go in separate NXentry groups, 
    this is a simple matter to change.)
    
    After each fly scan is save to the output HDF5 file, close
    its HDF raw data file.
    
    Close the output HDF5 file.
    '''
    data_files = '''
       Blank_20_1386638201.h5
       Blank_30_1386638026.h5
       Blank_45_1386637624.h5
       Blank_60_1386638396.h5
       Blank_120_1386638732.h5
       Adam_20_1386638251.h5
       Adam_30_1386638085.h5
       Adam_45_1386637699.h5
       Adam_60_1386638485.h5
       Adam_120_1386638883.h5
       PS_20_1386638301.h5
       PS_30_1386638146.h5
       PS_45_1386637773.h5
       PS_60_1386638575.h5
       PS_120_1386639035.h5
    '''.split()
    db = {}
    for filename in data_files:
        print 'Reading: ' + filename
        if filename.startswith('PS'):
            hdf = UsaxsFlyScanData(filename, bin_count=2500)
        else:
            hdf = UsaxsFlyScanData(filename, bin_count=300)
        key = os.path.splitext(filename)[0]
        db[key] = hdf
    if len(db) > 0:
        import eznx
        out = eznx.makeFile('2013-12-09-reduced.h5')
        entry = eznx.makeGroup(out, 'fly_2013_12_09', 'NXentry')
        for key, hdf in sorted(db.items()):
            print 'Saving: ' + key
            data = eznx.makeGroup(entry, key, 'NXdata')
            hdf.save_results(data)
            hdf.close_hdf_file()
        out.close()


def developer():
    # different development directories
    dir_list = [
                r'/data/USAXS_data/struckData',
                r'C:\Users\Pete\Desktop\2013-12-09 USAXS fly scan data',
                r'/home/oxygen/JEMIAN/Documents/2013-12-09 USAXS fly scan data',
                ]
    for path in dir_list:
        if os.path.exists(path):
            os.chdir(path)
            developer_main()
            break


if __name__ == '__main__':
    # developer parameters
#     sys.argv.append('/share1/USAXS_data/2014-02/02_11_test2_fly/S3_WholeScan.h5')
#     sys.argv.append('test_fly.h5')
#     sys.argv.append('-n')
#     sys.argv.append('250')
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
