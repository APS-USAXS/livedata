#!/usr/bin/env python

'''developer testing of reduceFlyScanData'''


import os                   #@UnusedImport
import glob                 #@UnusedImport
import localConfig          #@UnusedImport
import reduceFlyData        #@UnusedImport
from specplot import *      #@UnusedWildImport
import spec2nexus           #@UnusedImport
import numpy
import h5py
import math
import datetime

MCA_CLOCK_FREQUENCY = 50e6      # 50 MHz clock (not stored in older files)
ARCHIVE_SUBDIR_NAME = 'archive'
V_f_gain = localConfig.FIXED_VF_GAIN
FULL_REDUCED_DATASET = -1


def Prakash_test():
    os.chdir('testdata/2014-04')
    sd = spec2nexus.prjPySpec.SpecDataFile('04_09_Prakash.dat')
    os.chdir('04_09_Prakash_fly')
    print 'SPEC data file: ', sd.fileName
    for hdf_file_name in sorted(glob.glob('*.h5')):
        print '   FlyScan data file: ', hdf_file_name
        scanNum = int(hdf_file_name[1:hdf_file_name.find('_')])
        scan = sd.getScan(scanNum)
        hdf = reduceFlyData.UsaxsFlyScan(hdf_file_name)
        hdf.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
        plotData = zip(hdf.rebinned['Q'], hdf.rebinned['R'])
        pl = format_ploticus_data(plotData)
        dataFile = write_ploticus_data_file(pl['data'])
        plotFile = 'S%d_plot.png' % scanNum
        
        #---- execute the ploticus command file using a "prefab" plot style
        run_ploticus_command_script(scan, dataFile, plotData, plotFile)
        print '   FlyScan plot file: ', plotFile


def reduction_test():
    path = 'testdata/flyScanHdf5Files'
    for hdf_file_name in sorted(glob.glob(os.path.join(path, '*.h5'))):
        print '   FlyScan data file: ', hdf_file_name
        hdf = reduceFlyData.UsaxsFlyScan(hdf_file_name)
        hdf.reduce()
        hdf.save(hdf_file_name, True, False)
        #hdf.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
        #plotData = zip(hdf.rebinned['Q'], hdf.rebinned['R'])
        print 'done'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class UsaxsFlyScan(object):
    
    def __init__(self, hdf5_file_name):
        if not os.path.exists(hdf5_file_name):
            raise IOError, 'file not found: ' + hdf5_file_name
        self.hdf5_file_name = hdf5_file_name
        self.reduced = self.read_reduced()
    
    def reduce(self):
        '''convert raw Fly Scan data to R(Q), also get other terms'''
        hdf = h5py.File(self.hdf5_file_name, 'r')
        amp_name = get_USAXS_PD_amplifier_name(hdf)
        upd_ranges = revised__get_ranges(hdf, amp_name)
        upd_gain = get_gain(hdf, amp_name, upd_ranges)
        upd_dark = get_bkg(hdf, amp_name, upd_ranges)

        raw = hdf['entry/flyScan']

        raw_clock_pulses =  raw['mca1']
        raw_I0 =            raw['mca2']
        raw_upd =           raw['mca3']

        raw_num_points =    int(raw['AR_pulses'][0])
        AR_start =          raw['AR_start']
        AR_increment =      raw['AR_increment']
        raw_ar = AR_start - numpy.arange(raw_num_points) * AR_increment
        
        pulse_frequency = raw['mca_clock_frequency'][0] or  MCA_CLOCK_FREQUENCY
        channel_time_s = raw_clock_pulses / pulse_frequency
        
        # rVec = (pd_counts - seconds*dark_curr) / diode_gain / I0 / V_f_gain
#         rVec = (raw_upd - channel_time_s*upd_dark) / upd_gain / raw_I0 / V_f_gain
        upd = numpy.ma.masked_array(data=raw_upd, mask=upd_dark.mask)
        rVec = upd / upd_gain / raw_I0 / V_f_gain
        rVec *= 1e8

        d2r = math.pi / 180
        wavelength = hdf['/entry/instrument/monochromator/wavelength'][0]
        # simple sum since AR are equi-spaced
        arCenter = numpy.sum(raw_ar * rVec) / numpy.sum(rVec)
        qVec = (4 * math.pi / wavelength) * numpy.sin(d2r*(arCenter - raw_ar)/2)
        
        upd = numpy.array(raw_upd)
        i0 = numpy.array(raw_I0)
        dark = numpy.array(channel_time_s*upd_dark)
        hdf.close()

        hdf = h5py.File(self.hdf5_file_name, 'a')
        nxdata = reduceFlyData.h5_openGroup(hdf, '/entry/reduced', 'NXdata', timestamp=self.yyyymmdd_hhmmss())
        reduceFlyData.h5_write_dataset(nxdata, 'AR',       raw_ar,          units='degrees')
        reduceFlyData.h5_write_dataset(nxdata, 'upd',      upd,             units='counts')
        reduceFlyData.h5_write_dataset(nxdata, 'time',     channel_time_s,  units='s')
        reduceFlyData.h5_write_dataset(nxdata, 'dark',     dark,            units='counts')
        reduceFlyData.h5_write_dataset(nxdata, 'upd_dark', upd_dark,        units='counts/s')
        reduceFlyData.h5_write_dataset(nxdata, 'upd_gain', upd_gain,        units='n/a')
        reduceFlyData.h5_write_dataset(nxdata, 'I0',       i0,              units='counts')
        reduceFlyData.h5_write_dataset(nxdata, 'Q',        qVec,            units='1/A')
        reduceFlyData.h5_write_dataset(nxdata, 'R',        rVec,            units='n/a')
        hdf.close()

#         d = dict(Q=numpy.ma.masked_array(data=qVec, mask=rVec.mask).compressed(),
#                     R=rVec.compressed(), 
#                     AR=numpy.ma.masked_array(data=raw_ar, mask=rVec.mask).compressed(), 
#                     R_max=None, 
#                     AR_centroid=arCenter, 
#                     AR_FWHM=None)
        d = dict(Q=qVec,
                    R=rVec, 
                    AR=raw_ar, 
                    R_max=None, 
                    AR_centroid=arCenter, 
                    AR_FWHM=None)
        
        self.reduced = dict(full=d)
        return d
    
    def rebin(self, bin_count = None):
        if bin_count is None:
            bin_count = localConfig.REDUCED_FLY_SCAN_BINS

        # TODO: do the right thing here

        d = dict(Q=None, R=None, dR=None)
        self.reduced[str(bin_count)] = d
    
    def read_reduced(self):
        '''
        work-in-progress
        
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
                #print nxdata.name
                reduction_name = key[len('flyScan_reduced_'):]
                d = {}
                for dsname in fields:
                    if dsname in nxdata:
                        # extract the Numpy structure!
                        d[dsname] = nxdata[dsname]
                reduced[reduction_name] = d
        hdf.close()
        return reduced
    
    def save_reduced(self):
        if len(self.reduced) == 0:
            return
        hdf = h5py.File(self.hdf5_file_name, 'a')
        nxentry = reduceFlyData.h5_openGroup(hdf, 'entry', 'NXentry')
        for key, reduced_ds in self.reduced.items():
            nxdata = reduceFlyData.h5_openGroup(nxentry, 
                                                'flyScan_reduced_'+key, 
                                                'NXdata', 
                                                timestamp=self.yyyymmdd_hhmmss())
            for k, v in reduced_ds.items():
                # TODO: fix the units
                # TODO: do not save None datasets
                if v is not None:
                    reduceFlyData.h5_write_dataset(nxdata, k, v,  units='')
        hdf.close()

    def yyyymmdd_hhmmss(self):
        t = datetime.datetime.now()
        yyyymmdd = t.strftime("%Y-%m-%d")
        hhmmss = t.strftime("%H:%M:%S")
        return yyyymmdd + " " + hhmmss


def revised__get_ranges(hdf, identifier):
    '''
    local routine to setup the call
    
    :param obj hdf: opened HDF5 file instance
    :param str identifier: amplifier name, as stored in the HDF5 file
    '''
    num_channels = hdf['/entry/flyScan/AR_pulses'][0]
    base = '/entry/flyScan/changes_' + identifier + '_'
    arr_channel   = hdf[base + 'mcsChan']
    arr_requested = hdf[base + 'ampReqGain']
    arr_actual    = hdf[base + 'ampGain']

    return get_ranges(num_channels, arr_channel, arr_requested, arr_actual)


def construct_indexed_array(lookup_table, pd_ranges):
    '''
    return masked numpy array of length len(pd_ranges) with values from lookup_table

    :param [float] lookup_table: values for result array
    :param [int] pd_ranges: range index numbers of the photodiode
    
    Build a new masked numpy array from lookup_table 
    such that its values are indexed by pd_ranges.
    Masks in pd_ranges are preserved.
    ''' 
    n = len(pd_ranges)
    indexed_array = []
    for r in range(n):
        v = pd_ranges[r]
        # TODO: can this be more efficient?
        if isinstance(v, numpy.ma.core.MaskedConstant):
            v = 0
        else:
            v = lookup_table[v]
        indexed_array.append(v)
    return numpy.ma.masked_less_equal(indexed_array, 0)


def get_bkg(hdf, amplifier, pd_ranges):
    '''
    get backgrounds for named amplifier from the HDF5 file
    
    :param obj hdf: opened HDF5 file instance
    :param str amplifier: amplifier name, as stored in the HDF5 file
    :param [int] pd_ranges: range index numbers of the photodiode
    
    The masked numpy integer array pd_ranges has length equal to the number of
    bins in the acquired dataset.  The value of pd_ranges are between 0 and
    len(bkg)-1 inclusive, that is [0..4].
    '''
    base = '/entry/metadata/' + amplifier + '_bkg'
    bkg = [hdf[base+str(_)][0] for _ in range(5)]
    return construct_indexed_array(bkg, pd_ranges)


def get_gain(hdf, amplifier, pd_ranges):
    '''
    get gains for named amplifier from the HDF5 file
    
    :param obj hdf: opened HDF5 file instance
    :param str amplifier: amplifier name, as stored in the HDF5 file
    :param [int] pd_ranges: range index numbers of the photodiode
    
    The masked numpy integer array pd_ranges has length equal to the number of
    bins in the acquired dataset.  The value of pd_ranges are between 0 and
    len(gain)-1 inclusive, that is [0..4].
    '''
    base = '/entry/metadata/' + amplifier + '_gain'
    gain = [hdf[base+str(_)][0] for _ in range(5)]
    # now construct new array upd_gain from gain[pd_ranges], sort of,
    return construct_indexed_array(gain, pd_ranges)


def get_ranges(num_channels, arr_channel, arr_requested, arr_actual):
    '''
    return a numpy masked array of detector range changes
    
    mask_value is true during a range change when requested != actual
    mask_value is true for first and last point
    
    :param int num_channels: number of channels to create in MCS data array
    :param int arr_channel: array of channel numbers for range change events
    :param int arr_requested: array of requested amplifier ranges
    :param int arr_actual: array of actual amplifier ranges
    '''
    def assign_range_value(start, end, range_value):
        '''short-hand assignment'''
        if end - start >= 0:    # define the valid range
            ranges[start:end] = numpy.zeros((end - start,)) + range_value

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


def get_USAXS_PD_amplifier_name(hdf):
    base = '/entry/flyScan/upd_flyScan_amplifier'
    amp_index = hdf[base][0]
    labels = {0: base+'_ZNAM', 1: base+'_ONAM'}
    return str(hdf[labels[amp_index]][0])


def main():
    #reduction_test()
    
    for hdf_file_name in glob.glob(os.path.join('testdata', 'flyScanHdf5Files', '*.h5')):
        print hdf_file_name
        recomputed = False
        h = UsaxsFlyScan(hdf_file_name)
        if 'full' not in h.reduced:
            h.reduce()
            recomputed = True
        if recomputed or str(localConfig.REDUCED_FLY_SCAN_BINS) not in h.reduced:
            h.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
            recomputed = True
        if recomputed:
            h.save_reduced()


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
