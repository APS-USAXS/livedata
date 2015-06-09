#!/usr/bin/env python

'''reduceFlyScanData: reduce the raw data from USAXS Fly Scans to R(Q)'''

import datetime             #@UnusedImport
import h5py                 #@UnusedImport
import math                 #@UnusedImport
import numpy                #@UnusedImport
import os                   #@UnusedImport
import scipy.interpolate    #@UnusedImport
import shutil               #@UnusedImport
import stat                 #@UnusedImport
from spec2nexus import eznx #@UnusedImport
import calc
import localConfig          #@UnusedImport
import pvwatch
import ustep                #@UnusedImport


ARCHIVE_SUBDIR_NAME = 'archive'
DEFAULT_BIN_COUNT   = localConfig.REDUCED_FLY_SCAN_BINS
FIXED_VF_GAIN       = localConfig.FIXED_VF_GAIN
MCA_CLOCK_FREQUENCY = localConfig.MCA_CLOCK_FREQUENCY
Q_MIN               = localConfig.FLY_SCAN_Q_MIN
UATERM              = localConfig.FLY_SCAN_UATERM
ESD_FACTOR          = 0.01      # estimate dr = ESD_FACTOR * r  if r.std() = 0

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


class UsaxsFlyScan(object):
    '''
    reduce the raw data for one USAXS Fly Scan
    
    Goals
    =====
    
    * reduce the raw USAXS data to standard I(Q)
    * read raw data
    * reconstruct AR
    * reconstruct R(ar)
    * compute Q from AR
    * rebin data to desired size and Q range
    
    Primary Input Data
    ==================
    
    The primary input data for this class is an HDF file produced by
    *saveFlyData.py*.  The principal contents are:
    
    * several channels from a multi-channel scaler (MCS)
    * arrays of when the photodiode amplifier range changed
    * various metadata about detector, instrument, user, and sample
    
    A USAXS Fly Scan is generated by creating an array of
    waypoints for the AR stage to reach at regular time intervals.
    The waypoint array is generated from SPEC and forms the
    primary motion profile for the scan.  Other motors, AY and DY,
    are slaved to this profile and moved accordingly.
    
    The progress of AR motion is measured as a stream of pulses
    from the Aerotech Ensemble motor controller.  A pulse is emitted
    for a specified increment of AR encoder position.  The increment
    (:math:\Delta E_{ar}`) is a parameter specified in the metadata.
    The pulses are used to advance the channel pointer of the MCS.
    
    Each MCS channel, :math:`i`, corresponds to one specific AR encoder position.
    The AR encoder position array is reconstructed:
    
    .. math:: AR[i] = AR_{start} - i \times\  \Delta E_{ar}
    
    where :math:`AR_{start}` is the starting AR position.
    
    .. note::  Note the *minus* sign in the previous equation!
    
    The various input signals to the MCS are:
    
    * clock (:math:`p_t`)
    * monitor pulses (:math:`p_m`)
    * detector pulses (:math:`p_d`)
    
    The measurement time spent in any single channel, :math:`i`, of the MCS is calculated:
    
    .. math:: t[i] = p_t[i] f_{clock}
    
    where :math`f_{clock}` is the clock frequency (also recorded in the metadata).
    
    The count rate for the monitor is calculated:
    
    .. math:: M[i] = p_m[i] / t[i]
    
    The count rate for the detector is calculated:
    
    .. math:: D[i] = p_d[i] / t[i]
    
    The detector signal is modified by the detector amplifier gain, :math:`A`,
    which is selected by the amplifier range, :math:`r`, (an integer number from 0 to 4)
    and also by the inherent background of the selected amplifier range, :math:`B`.
    
    .. caution:  Describe how :math:`r` is obtained.  Also describe data masking.
    
    .. note:: Actually, the monitor also has a gain and background which is 
       patterned on the same terms for the detector signal
    
    The ratio intensity, :math:`R`, is calculated as the ratio of the two corrected count rates
    (where subscripts :math:`d` and :math:`m` refer to detector and monitor, respectively): 
    
    .. math:: R[i] = { ( A_d[r[i]] * ( D[i] - B_d[r[i]] ) \over ( A_m[r[i]] * ( M[i] - B_m[r[i]] ) }
    
    Data from the HDF5 file
    =======================
    
    =====================  ======================================================  ===========================================================
    term                   HDF address path                                        description
    =====================  ======================================================  ===========================================================
    :math:`n`              /entry/flyScan/AR_pulses                                number of data points in MCA arrays
    :math:`p_t`            /entry/flyScan/mca1                                     array of clock pulses
    :math:`p_m`            /entry/flyScan/mca2                                     array of monitor pulses
    :math:`p_d`            /entry/flyScan/mca3                                     array of detector pulses
    :math:`f_{clock}`      /entry/flyScan/mca_clock_frequency                      MCA clock frequency
    :math:`AR_{start}`     /entry/flyScan/AR_start                                 AR starting position
    :math:`\Delta E_{ar}`  /entry/flyScan/AR_increment                             AR channel increment
    changes_mcsChan        /entry/flyScan/changes_AMP_mcsChan                      array of MCS channels for range change events
    changes_ampGain        /entry/flyScan/changes_AMP_ampGain                      array of AMPlifier range change events (provides :math:`r`)
    changes_ampReqGain     /entry/flyScan/changes_AMP_ampReqGain                   array of requested AMPlifier range change events
    :math:`A[0]`           /entry/metadata/upd_gain0                               amplifier gain for range 0
    :math:`A[1]`           /entry/metadata/upd_gain1                               amplifier gain for range 1
    :math:`A[2]`           /entry/metadata/upd_gain2                               amplifier gain for range 2
    :math:`A[3]`           /entry/metadata/upd_gain3                               amplifier gain for range 3
    :math:`A[4]`           /entry/metadata/upd_gain4                               amplifier gain for range 4
    :math:`B[0]`           /entry/metadata/upd_bkg0                                amplifier background count rate for range 0
    :math:`B[1]`           /entry/metadata/upd_bkg1                                amplifier background count rate for range 1
    :math:`B[2]`           /entry/metadata/upd_bkg2                                amplifier background count rate for range 2
    :math:`B[3]`           /entry/metadata/upd_bkg3                                amplifier background count rate for range 3
    :math:`B[4]`           /entry/metadata/upd_bkg4                                amplifier background count rate for range 4
    =====================  ======================================================  ===========================================================

    example::
    
        hfile = 'some/HDF5/testfile.h5'
        ufs = UsaxsFlyScan(hfile)
        ufs.make_archive()
        #ufs.read_reduced()
        ufs.reduce()
        ufs.rebin(250)
        ufs.save(hfile, 'full')
        ufs.save(hfile, 250)

    '''
    
    def __init__(self, hdf5_file_name):
        if not os.path.exists(hdf5_file_name):
            raise IOError, 'file not found: ' + hdf5_file_name

        self.units = dict(
            ar = 'degrees',
            upd_ranges = '',
            Q = '1/A',
            R = 'none',
            dR = 'none', 
            R_max = 'none',
            AR_R_peak = 'degrees',
            ar_r_peak = 'degrees',
            r_peak = 'none',
            ar_0 = 'degrees',
            fwhm = 'degrees',
        )
        self.min_step_factor = 1.5
        self.uaterm = UATERM
        self.bin_count = DEFAULT_BIN_COUNT

        self.hdf5_file_name = hdf5_file_name
        self.reduced = {}
        
    def has_reduced(self, key = 'full'):
        '''
        check if the reduced dataset is available
        
        :param str|int key: name of reduced dataset (default = 'full')
        '''
        if key not in self.reduced:
            return False
        return 'Q' in self.reduced[key] and 'R' in self.reduced[key]

    def reduce(self):
        '''convert raw Fly Scan data to R(Q), also get other terms'''
        if not os.path.exists(self.hdf5_file_name):
            raise IOError, 'file not found: ' + self.hdf5_file_name
        hdf = h5py.File(self.hdf5_file_name, 'r')
    
        pname = self.get_program_name(hdf)
        config_version = self.get_config_version(pname)
        mode_number = self.get_mode_number(hdf, config_version)
        _mode_name = self.get_mode_name(mode_number)

        raw = hdf['entry/flyScan']

        wavelength = float(hdf['/entry/instrument/monochromator/wavelength'][0])
        ar_center  = float(hdf['/entry/metadata/AR_center'][0])

        raw_clock_pulses =  raw['mca1']
        raw_I0 =            raw['mca2']
        raw_upd =           raw['mca3']

        AR_start =          float(raw['AR_start'][0])
        AR_increment =      float(raw['AR_increment'][0])

        # compute the AR values from the MCA waveforms
        raw_ar = self.get_raw_ar(hdf, mode_number)

        V_f_gain = FIXED_VF_GAIN
        pulse_frequency = raw['mca_clock_frequency'][0] or  MCA_CLOCK_FREQUENCY
        channel_time_s = raw_clock_pulses / pulse_frequency
        
        amp_name = self.get_USAXS_PD_amplifier_name(hdf)
        upd_ranges = self.get_ranges(hdf, amp_name)
        upd_ranges = self.apply_upd_range_change_time_mask(hdf, upd_ranges, channel_time_s)
        gains = self.get_gain(hdf, amp_name)
        bkg   = self.get_bkg(hdf, amp_name)

        upd_gain = get_channels_from_signals_and_ranges(gains, upd_ranges)
        upd_dark = get_channels_from_signals_and_ranges(bkg,   upd_ranges)
        
        I0_amp_gain = float(hdf['/entry/metadata/I0AmpGain'][0])
        
        if mode_number in (AR_MODE_ARRAY, AR_MODE_TRAJECTORY):
            # consequence of Aerotech HLe providing no useful data in 1st channel
            upd_ranges = upd_ranges[1:]
            upd_gain = upd_gain[1:]
            upd_dark = upd_dark[1:]
            # truncate in case PSO oscillations were corrected
            n = len(raw_upd)
            upd_ranges = upd_ranges[:n]
            upd_gain = upd_gain[:n]
            upd_dark = upd_dark[:n]
        
        # ensure arrays have equal lengths
        list_of_arrays = [raw_upd, channel_time_s, upd_dark, upd_gain, raw_ar, raw_I0]
        min_n = min(map(len, list_of_arrays))
        max_n = max(map(len, list_of_arrays))
        if min_n != max_n:      # truncate arrays to shortest length
            n = min(min_n, max_n)
            pvwatch.logMessage( "  truncating all arrays to " + str(n) + " points" )
            raw_upd         = raw_upd[:n]
            channel_time_s  = channel_time_s[:n]
            upd_dark        = upd_dark[:n]
            upd_gain        = upd_gain[:n]
            raw_ar          = raw_ar[:n]
            raw_I0          = raw_I0[:n]
    
        full = calc.calc_R_Q(wavelength, raw_ar, channel_time_s, raw_upd, upd_dark, upd_gain, 
                             raw_I0, I0_gain=I0_amp_gain)
        center = full['ar_0']

        hdf.close()
        
        full['R_max'] = full['R'].max()
        self.reduced = dict(full = full)
    
    def PSO_oscillation_correction(self, hdf, mode, num_AR):
        '''
        compute array new AR values from 10Hz encoder sampling
        
        :param h5py.File hdf: HDF5 file object with the fly scan data
        :param int mode: one of these [AR_MODE_ARRAY, AR_MODE_TRAJECTORY]
        :param int num_AR: length of new AR array
        :return numpy.array: array of computed ar values
        
        The Aerotech HLe and the AR encoder together are sensitive to vibrations
        of the USAXS table and environment.  The sensitivity appears as jitter in 
        the PSO pulse train and renders the reported array of AR positions wrong.
        The best fix for this, to date, is to re-compute the AR values based
        on AR encoder values sampled at 10Hz from EPICS.  Here's how:

        * get the AR encoder v. PSO pulse data from the 10 Hz arrays
        * interpolate AR(PSO) at each desired PSO

        Good luck.
        '''
        if mode not in (AR_MODE_ARRAY, AR_MODE_TRAJECTORY):
            msg = 'PSO_oscillation_correction: wrong mode = ' + str(mode)
            raise ValueError, msg
        
        # TODO: find better way to report this information
        #print "  possible vibrations during scan, re-generating AR from 10Hz sampling array"
        pso, ar = self.getAR_10Hz_Array(hdf)

        linear_interpolation_func = scipy.interpolate.interp1d(pso, ar)
        new_ar = linear_interpolation_func(range(num_AR))
        return new_ar

    def rebin(self, bin_count = None):
        '''generate R(Q) with a bin_count bins, save in ``self.reduced[str(bin_count)]`` dict'''

        def subarray(arr, key_arr, lo, hi):
            '''return subarray of arr where lo < arr <= hi'''
            low_pass  = numpy.where(key_arr <= hi, arr,      0)
            high_pass = numpy.where(lo < key_arr,  low_pass, 0)
            return numpy.trim_zeros(high_pass)
        
        if not self.has_reduced():
            self.reduce()

        bin_count = bin_count or self.bin_count
        s = str(bin_count)
        
        Q_full = self.reduced['full']['Q']
        R_full = self.reduced['full']['R']
        
        # lowest non-zero Q value > 0 or minimum acceptable Q
        Qmin = max(Q_MIN, Q_full[numpy.where(Q_full > 0)].min() )
        Qmax = 1.0001 * Q_full.max()
        
        # pick smallest Q step size from input data, scale by a factor
        minStep = self.min_step_factor * numpy.min(Q_full[1:] - Q_full[:-1])
        # compute bin edges from ustep
        Q_bins = numpy.array(ustep.ustep(Qmin, 0.0, Qmax, bin_count+1, self.uaterm, minStep).series)
        qVec, rVec, drVec = [], [], []
        for xref in bin_xref(Q_full, Q_bins):
            if len(xref) > 0:
                q = Q_full[xref]
                r = R_full[xref]
                if r.min() <= 0:    # TODO: fix this in reduce()
                    r = numpy.ma.masked_less_equal(r, 0)
                    q = calc.remove_masked_data(q, r.mask)
                    r = calc.remove_masked_data(r, r.mask)
                if q.size > 0:
                    qVec.append(  numpy.exp(numpy.mean(numpy.log(q))) ) 
                    rVec.append(  numpy.exp(numpy.mean(numpy.log(r))) )
                    dr = r.std()
                    if dr == 0.0:
                        drVec.append( ESD_FACTOR * rVec[-1] )
                    else:
                        drVec.append( r.std() )

        reduced = dict(
            Q  = numpy.array(qVec),
            R  = numpy.array(rVec),
            dR = numpy.array(drVec),
        )
        self.reduced[s] = reduced
        return reduced

    def read_reduced(self):
        '''
        read any and all reduced data from the HDF5 file, return in a dictionary
        
        dictionary = {
          'full': dict(Q, R, R_max, ar, fwhm, centroid)
          '250':  dict(Q, R, dR)
          '5000': dict(Q, R, dR)
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
                d = {}
                for dsname in fields:
                    if dsname in nxdata:
                        value = nxdata[dsname]
                        if value.size == 1:
                            d[dsname] = float(value[0])
                        else:
                            d[dsname] = numpy.array(value)
                reduced[nxname] = d
        hdf.close()
        self.reduced = reduced
        return reduced
    
    def save(self, hfile = None, key = None):
        '''
        save the reduced data group to an HDF5 file, return filename or None if not written
        
        :param str hfile: output HDF5 file name (default: input HDF5 file)
        :param str key: name of reduced data set (default: nothing will be saved)
        
        By default, save to the input HDF5 file.
        To override this, specify the output HDF5 file name when calling this method.
        
        * If the file exists, this will not overwrite any input data.
        * Full, reduced :math:`R(Q)` goes into NXdata group::
        
            /entry/flyScan_reduced_full
        
        * any previous full reduced :math:`R(Q)` will be replaced.
        
        * It may replace the rebinned, reduced :math:`R(Q)` 
          if a NXdata group of the same number of bins exists.
        * Rebinned, reduced :math:`R(Q)`  goes into NXdata group::
          
              /entry/flyScan_reduced_<N>
        
          where ``<N>`` is the number of bins, such as (for 500 bins):: 
          
              /entry/flyScan_reduced_500
        
        :see: http://download.nexusformat.org/doc/html/classes/base_classes/NXentry.html
        :see: http://download.nexusformat.org/doc/html/classes/base_classes/NXdata.html
        '''
        key = str(key)
        if key not in self.reduced:
            return
        nxname = 'flyScan_reduced_' + key
        hfile = hfile or self.hdf5_file_name
        ds = self.reduced[key]
        hdf = h5py.File(hfile, 'a')
        nxentry = eznx.openGroup(hdf, 'entry', 'NXentry')
        nxdata = eznx.openGroup(nxentry, nxname, 'NXdata', timestamp=self.iso8601_datetime())
        for key in sorted(ds.keys()):
            try:
                _ds = eznx.write_dataset(nxdata, key, ds[key])
                if key in self.units:
                    eznx.addAttributes(_ds, units=self.units[key])
            except RuntimeError, e:
                pass        # TODO: reporting
        hdf.close()
        return hfile
        
    def get_program_name(self, hdf):
        if 'program_name' not in  hdf['/entry']:
            msg = 'no /entry/program_name in file: ' + self.hdf5_file_name
            raise KeyError(msg)
        return hdf['/entry/program_name']
        
    def get_config_version(self, pname):
        if 'config_version' in pname.attrs:
            config_version = pname.attrs['config_version']
        else:
            config_version = '1'
        return config_version
        
    def get_mode_number(self, hdf, config_version):
        if config_version in ('1', '1.0'):
            mode_number = 0
        elif config_version in ('1.1', '1.2'):
            mode_number = hdf['/entry/flyScan/AR_PulseMode'][0]
        else:
            hdf.close()
            msg = "Unexpected /entry/program_name/@config_version = " + config_version
            raise ValueError, msg
        return mode_number
        
    def get_mode_name(self, mode_number):
        if mode_number in MODENAME_XREF:
            # just in case this is useful
            _mode_name = MODENAME_XREF[mode_number]
        else:
            msg = 'Unexpected /entry/flyScan/AR_PulseMode value = ' + str(mode_number)
            raise ValueError, msg
        return _mode_name
    
    def get_raw_ar(self, hdf, mode_number):
        raw = hdf['entry/flyScan']
        raw_num_points = int(raw['AR_pulses'][0])
        AR_start =       float(raw['AR_start'][0])

        if mode_number == AR_MODE_FIXED:      # often more than ten thousand points
            AR_increment = float(raw['AR_increment'][0])
            raw_ar = AR_start - numpy.arange(raw_num_points) * AR_increment
            PSO_oscillations_found = False
        
        elif mode_number in (AR_MODE_ARRAY, AR_MODE_TRAJECTORY):
            keymap = {AR_MODE_ARRAY: '/entry/flyScan/AR_PulsePositions',    # a few thousand points
                      AR_MODE_TRAJECTORY: '/entry/flyScan/AR_waypoints'}    # a few hundred points
            raw_ar = numpy.array(hdf[keymap[mode_number]])
            raw_ar = raw_ar - raw_ar[0] + AR_start
            if len(raw_ar) > raw_num_points:
                raw_ar = raw_ar[:raw_num_points]   # truncate unused bins, if needed
            
            # note: Aerotech HLe system does not report any data for first channel.
            #       Shift data to have mean AR value for each point,
            #       not the end of the AR value, when the system advanced to next point.
            raw_ar = (raw_ar[1:] + raw_ar[:-1])/2    # midpoint of each interval
            raw_clock_pulses =  raw['mca1']
            PSO_oscillations_found = len(raw_clock_pulses) != len(raw_ar)

        if PSO_oscillations_found:
            # Aerotech's Position Synchronized Output (PSO) feature
            raw_ar = self.PSO_oscillation_correction(hdf, mode_number, len(raw_clock_pulses))
        
        return raw_ar
    
    def getAR_10Hz_Array(self, hdf):
        '''
        return arrays of AR encoder v. PSO pulse

        :param h5py.File hdf: HDF5 file object with the fly scan data
        :return (numpy.array,numpy.array): (pso, ar) arrays

        read the AR encoder positions sampled in EPICS at 10Hz
        these are recorded with the corresponding PSO pulse number
        '''
        ch_angle    = hdf['/entry/flyScan/changes_AR_angle']
        ch_PSOpulse = hdf['/entry/flyScan/changes_AR_PSOpulse']
        
        # for every PSO channel, make a list of all ar values
        # use a temporary dictionary for this
        channel = {}
        n = len(ch_PSOpulse.value)
        for index in range(n):
            x = ch_PSOpulse[index]
            y = ch_angle[index]
            if x not in channel:
                channel[x] = []
            if len(channel)>1 and x == 0.0:
                break       # all useful channels received, ignore remaining buffer
            channel[x].append(y)
        
        pso = sorted(channel.keys())
        if pso[0] != 0.0:
            msg = '1st PSO pulse in 10Hz array is not zero'
            raise ValueError, msg
        # first PSO channel 0 may be repeated, keep the last one
        channel[0.0] = channel[0.0][-1]
        # last PSO channel may be repeated, keep the first one
        index = pso[-1]       # index of the last channel
        channel[index] = channel[index][0]
        
        # average all the other channels, x:PSO, y:AR
        for x, y in channel.items():
            if isinstance(y, list):     # list items have not been handled yet
                if len(y) == 1:
                    channel[x] = y[0]
                else:
                    channel[x] = numpy.array(y).mean()

        ar = map(lambda xx: channel[xx], pso) # map() is faster than this:  [channel[_] for _ in pso]
        
        return numpy.array(pso), numpy.array(ar)

    def get_USAXS_PD_amplifier_name(self, hdf):
        '''return the name of the chosen USAXS photodiode amplifier'''
        base = '/entry/flyScan/upd_flyScan_amplifier'
        amp_index = hdf[base][0]
        labels = {0: base+'_ZNAM', 1: base+'_ONAM'}
        return str(hdf[labels[amp_index]][0])
    
    def get_range_changes(self, hdf, ampName):
        '''get the arrays of range change information for the named amplifier'''
        #num_channels = hdf['/entry/flyScan/AR_pulses'][0]    # planned length
        base = '/entry/flyScan/changes_' + ampName + '_'
        arr_channel   = hdf[base + 'mcsChan']
        arr_requested = hdf[base + 'ampReqGain']
        arr_actual    = hdf[base + 'ampGain']
        return arr_channel, arr_requested, arr_actual

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
    
        #num_channels = hdf['/entry/flyScan/AR_pulses'][0]    # planned length
        num_channels = len(hdf['/entry/flyScan/mca1'])        # actual length
        arr_channel, arr_requested, arr_actual = self.get_range_changes(hdf, identifier)
    
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
        base = '/entry/metadata/' + amplifier + '_gain'
        gain = map(lambda x: hdf[base+str(x)][0], range(5))
        return gain
    
    
    def get_bkg(self, hdf, amplifier):
        '''
        get backgrounds for named amplifier from the HDF5 file
        
        :param obj hdf: opened HDF5 file instance
        :param str amplifier: amplifier name, as stored in the HDF5 file
        '''
        base = '/entry/metadata/' + amplifier + '_bkg'
        bkg = map(lambda x: hdf[base+str(x)][0], range(5))
        return bkg
    
    def apply_upd_range_change_time_mask(self, hdf, upd_ranges, channel_time_s):
        '''
        apply mask for specified time after a range change
        
        :param obj hdf: open FlyScan data file (h5py File object)
        :param obj upd_ranges: photodiode amplifier range (numpy masked ndarray)
        :param obj channel_time_s: measurement time in each channel, s (numpy ndarray)
        '''
        # :param [float] mask_times: elapsed time after after range change 
        #                            in which data should be masked
        # mask is applied to pd_ranges
        base = '/entry/metadata/upd_amp_change_mask_time'
        mask_times = map(lambda r: float(hdf[base + str(r)][0]), range(5))
        amp_name = self.get_USAXS_PD_amplifier_name(hdf)
        changes = self.get_range_changes(hdf, amp_name)

        # modify the masks on upd_ranges at start of each range change
        length = len(channel_time_s)
        for channel, requested, actual in zip(*changes):
            i = int(channel)
            if i == 0:
                continue
            if requested != actual:
                upd_ranges[i] = numpy.ma.masked               # mask this point
                continue
            timer = mask_times[int(actual)]
            while timer > 0 and channel < length:
                upd_ranges[i] = numpy.ma.masked               # mask this point
                timer = max(0, timer - channel_time_s[i])     # decrement the time of this channel
                i += 1

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
        
    def make_archive(self):
        '''
        archive the original data before writing new items to it
        
        This method checks for the presence of such a file in 
        a subdirectory below the HDF5 file.  If found there, 
        this method does nothing.  If not found, this method creates
        the subdirectory (if necessary) and copies the HDF5 to
        that subdirectory and makes the HDF5 file there to be read-only.
        '''
        result = None
        path, hfile = os.path.split(self.hdf5_file_name)
        archive_dir = os.path.join(path, ARCHIVE_SUBDIR_NAME)
        archive_file = os.path.join(archive_dir, hfile)
        if not os.path.exists(archive_dir):
            os.mkdir(archive_dir)
        if not os.path.exists(archive_file):
            shutil.copy2(self.hdf5_file_name, archive_file)      # copy hfile to archive_file
            mode = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            os.chmod(archive_file, mode)           # make archive_file read-only to all
            result = archive_file
        return result
    
    def iso8601_datetime(self):
        '''return current date & time as modified ISO8601=compliant string'''
        t = datetime.datetime.now()
        # standard ISO8601 uses 'T', blank space instead is now allowed
        s = str(t).split('.')[0]
        return s

        
def get_channels_from_signals_and_ranges(signal, ranges):
    '''convert signal and upd amplifier ranges to value for channel'''
    channels = numpy.array([0,] + signal)[ranges.data+1]
    channels = numpy.ma.masked_less_equal(channels, 0)
    return channels


def bin_xref(x, bins):
    '''
    Return an array of arrays.  
    Outer array is in bins, inner array contains indices of x in each bin,
    
    :param ndarray x: values to be mapped
    :param ndarray bins: new bin boundaries
    '''
    indices = numpy.digitize(x, bins)
    xref_dict = {}
    for i, v in enumerate(indices):
        if 0 < v < len(bins):
            if str(v) not in xref_dict:
                xref_dict[str(v)] = []
            xref_dict[str(v)].append(i)
    key_list = map(int, xref_dict.keys())
    xref = [xref_dict[str(key)] for key in sorted(key_list)]
    return numpy.array(xref)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_user_options():
    '''parse the command line for the user options'''
    import argparse
    parser = argparse.ArgumentParser(prog='reduceUsaxsFlyScan', description=__doc__)
    parser.add_argument('hdf5_file', 
                        action='store', 
                        help="NeXus/HDF5 data file name")
    msg =  'how many bins in output R(Q)?'
    msg += '  (default = %d)' % DEFAULT_BIN_COUNT
    parser.add_argument('-n', 
                        '--num_bins',
                        dest='num_bins',
                        type=int,
                        default=DEFAULT_BIN_COUNT,
                        help=msg)
    msg =  'output file name?'
    msg += '  (default = input HDF5 file)'
    parser.add_argument('-o', 
                        '--output_file',
                        dest='output_file',
                        type=str,
                        default='',
                        help=msg)
    parser.add_argument('-V', 
                        '--version', 
                        action='version', 
                        version='$Id$')

    parser.add_argument('--recompute-full',
                        dest='recompute_full',
                        action='store_true',
                        default=False,
                        help='(re)compute full R(Q): implies --recompute-rebinning')

    parser.add_argument('--recompute-rebinned',
                        dest='recompute_rebinned',
                        action='store_true',
                        default=False,
                        help='(re)compute rebinned R(Q)')

    msg = 'do NOT archive the original file before saving R(Q)'
    parser.add_argument('--no-archive',
                        dest='no_archive',
                        action='store_true',
                        default=False,
                        help=msg)

    return parser.parse_args()


def command_line_interface():
    '''standard command-line interface'''
    cmd_args = get_user_options()

    if len(cmd_args.output_file) > 0:
        output_filename = cmd_args.output_file
    else:
        output_filename = cmd_args.hdf5_file
    s_num_bins = str(cmd_args.num_bins)

    needs_calc = {}
    pvwatch.logMessage( "Reading USAXS FlyScan data file: " + cmd_args.hdf5_file )
    scan = UsaxsFlyScan(cmd_args.hdf5_file)
    
    # 2015-06-08,prj: no need for archives now
    #if cmd_args.no_archive:
    #    print '  skipping check for archived original file'
    #else:
    #    afile = scan.make_archive()
    #    if afile is not None:
    #        print '  archived original file to ' + afile

    pvwatch.logMessage( '  checking for previously-saved R(Q)' )
    scan.read_reduced()
    needs_calc['full'] = not scan.has_reduced('full')
    if cmd_args.recompute_full:
        needs_calc['full'] = True
    needs_calc[s_num_bins] = not scan.has_reduced(s_num_bins)
    if cmd_args.recompute_rebinned:
        needs_calc[s_num_bins] = True
    needs_calc['250'] = True    # FIXME: developer only

    if needs_calc['full']:
        pvwatch.logMessage('  reducing FlyScan to R(Q)')
        scan.reduce()
        pvwatch.logMessage( '  saving reduced R(Q) to ' + output_filename)
        scan.save(cmd_args.hdf5_file, 'full')
        needs_calc[s_num_bins] = True
    if needs_calc[s_num_bins]:
        pvwatch.logMessage( '  rebinning R(Q) (from %d) to %d points' % (scan.reduced['full']['Q'].size, cmd_args.num_bins) )
        scan.rebin(cmd_args.num_bins)
        pvwatch.logMessage( '  saving rebinned R(Q) to ' + output_filename )
        scan.save(cmd_args.hdf5_file, s_num_bins)


if __name__ == '__main__':
    command_line_interface()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

