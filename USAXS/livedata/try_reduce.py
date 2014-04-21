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
    return hdf[labels[amp_index]][0]


def main():
    #reduction_test()
    
    for hdf_file_name in glob.glob(os.path.join('testdata', 'flyScanHdf5Files', '*.h5')):
        print hdf_file_name
        hdf = h5py.File(hdf_file_name, 'r')
        amp_name = get_USAXS_PD_amplifier_name(hdf)
        print 'uses USAXS_PD amplifier:', amp_name
        # for key in ('DDPCA300', 'DLPCA200', 'I00', 'I0'):
        #     print key, revised__get_ranges(hdf, key)
        print amp_name, revised__get_ranges(hdf, amp_name)
        hdf.close()


if __name__ == '__main__':
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
