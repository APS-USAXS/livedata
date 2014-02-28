#!/usr/bin/env python

'''reduceFlyScanData: reduce the raw data from USAXS Fly Scans to R(Q)'''

import os
import sys
import math
import numpy
import scipy.linalg
import h5py
from spec2nexus import eznx


MCA_CLOCK_FREQUENCY = 50e6      # 50 MHz clock (not stored in older files)
DEFAULT_BIN_COUNT   = 500


def get_data(parent, dataset_name, astype=None):
    '''get the numpy data from the HDF5 dataset, option to return as different numpy data type'''
    try:
        dataset = parent[dataset_name]
    except KeyError:
        return None
    dtype = dataset.dtype
    if astype is not None:
        dtype = astype
    if len(dataset.shape) > 1:
        raise RuntimeError, "unexpected %d-D data" % len(dataset.shape)
    if dataset.size > 1:
        return dataset[...].astype(dtype)   # as array
    else:
        return dataset[0].astype(dtype)     # as scalar


def get_channel_range_changes(hdf, raw_num_points):
    '''
    determine the range for each channel_now, mask during range changes, return a dict

    .. caution:: The algorithm here assumes that the monitor has a fixed 
       amplifier gain (an assumption that may be changed).
    
    A range change is identified when the requested range (of the amplifier)
    does not match the actual range.
    
    **example range change data**

    ======  ===  =====
    chan    req  range_now
    ======  ===  =====
    0       0    0
    0       1    0
    0       1    1
    12      0    1
    14      0    0
    77      1    0
    78      1    1
    102     2    1
    104     2    2
    2478    3    2
    2528    3    3
    0       0    0
    0       0    0
    ...
    ======  ===  =====
    
    This will be interpreted as:
    
    =====  ==================
    range  channels
    =====  ==================
    1      0-12
    0      14-77
    1      78-102
    2      104-2478
    3      2528-last channel_now
    =====  ==================
    
    and an ignore mask will be applied to channels: 0, 12-14, 77-78, 102-104, 2478-2528
    '''

    def _get_changes_data(identifier):
        return get_data(hdf, '/entry/flyScan/changes_'+identifier, astype=int)

    # get the data about range changes from HDF5 paths
    change_arrays = map(_get_changes_data, ('mcsChan', 'ampReqGain', 'ampGain'))

    channel_change_start, channel_last, range_last = -1, -1, -1
    ranges, changes = [], []
    # transpose the range change events and parse by rows
    for channel_now, range_requested, range_now in zip(*change_arrays):
        if channel_now == 0 and channel_last > 0:
            break
        
        if range_last != range_now:
            # mark a range change
            ranges.append((channel_now, range_now))
            if channel_change_start >= 0:
                # document start and end channels fo a range change
                changes.append((channel_change_start, channel_now))
            range_last = range_now
        
        if range_requested != range_now:
            # note that a range change was requested
            channel_change_start = channel_now
        
        channel_last = channel_now
        
    # rewrite ranges to mark start, end, range for each
    ranges.append((raw_num_points, -1))
    buf = []
    for i in range(len(ranges)-1):
        if ranges[i][0] == ranges[i+1][0]:
            continue
        buf.append((ranges[i][0], ranges[i+1][0], ranges[i][1]))
        if ranges[i+1][1] == -1:
            break
    ranges = buf
    
    return dict(ranges=ranges, changes=changes)
    
    
def calc_time_mask_channels(range_number, channel_start, channel_time_s, mask_times):
    '''return the end channel to mask for a change to the specified amplifier range'''
    elapsed = 0
    final_time = mask_times[range_number]
    for i in range(channel_start, channel_time_s.size):
        if elapsed >= final_time:
            break
        elapsed += channel_time_s[i]
    return i


def get_gains_bkg(hdf, raw_num_points, channel_time_s):
    '''get the amplifier gains and backgrounds for each data point'''
    def _get_meta(hdf_path_name):
        return get_data(hdf, hdf_path_name)
    def _get_meta_gain(identifier):
        return _get_meta('/entry/metadata/upd_gain'+str(identifier))
    def _get_meta_bkg(identifier):
        return _get_meta('/entry/metadata/upd_bkg'+str(identifier))

    amp_range_changes = get_channel_range_changes(hdf, raw_num_points)
    mask_times = get_range_change_mask_times(hdf)
    # get the table of amplifier gains and measured backgrounds
    gains_db = numpy.array(map(_get_meta_gain, range(5)))
    bkg_db = numpy.array(map(_get_meta_bkg, range(5)))  # counts/s
    
    ranges = numpy.ma.array(
                data=numpy.zeros((raw_num_points,),
                dtype='int8'),
                mask=numpy.ma.nomask, )

    # assign detector amplifier ranges
    for channel_start, channel_end, range_number in amp_range_changes['ranges']:
        ranges[channel_start:channel_end] = range_number

    # always apply changes _after_ data assignments
    for channel_start, channel_end in amp_range_changes['changes']:
        ranges[channel_start:channel_end] = numpy.ma.masked
        ranges[channel_end] = numpy.ma.masked      # also mask the ending point
        # mask for specified time _after_ the range change
        c1 = channel_end
        c2 = calc_time_mask_channels(ranges.data[channel_end], c1, channel_time_s, mask_times)
        ranges[c1:c2] = numpy.ma.masked
        ranges[c2] = numpy.ma.masked

    bkg = channel_time_s * bkg_db[ranges]
    gain = numpy.ma.masked_array(data=gains_db[ranges], mask=ranges.mask)
    return gain, bkg


def get_range_change_mask_times(hdf):
    '''get the interval to mask data after each amplifier range change'''
    def _get_mask_data(identifier):
        prefix = '/entry/flyScan/upd_amp_change_mask_time'
        return get_data(hdf, prefix+str(identifier))

    try:
        mask_times = map(_get_mask_data, range(5))
    except KeyError, exc:
        # default values
        mask_times = numpy.array((0, 0, 0, 0, 0.4), 'float')
        #mask_times = numpy.array((1, 1, 1, 1, 2), 'float')
    return mask_times


def FWHM(X,Y):
    '''http://stackoverflow.com/questions/10582795/finding-the-full-width-half-maximum-of-a-peak'''
    half_max = max(Y) / 2.
    #find when function crosses line half_max (when sign of diff flips)
    #take the 'derivative' of signum(half_max - Y[])
    d = numpy.sign(half_max - numpy.array(Y[0:-1])) - numpy.sign(half_max - numpy.array(Y[1:]))
    #plot(X,d) #if you are interested
    #find the left and right most indexes
    left_idx = numpy.argwhere(d > 0).flatten()[0]
    right_idx = numpy.argwhere(d < 0).flatten()[-1]
    return abs(X[right_idx] - X[left_idx])    #return the difference (full width)


def compute_Q_centroid_and_Rmax(hdf, ar, ratio, centroid = None):
    '''compute Q, also compute some terms involving the central peak, return in a dict'''
    numpy_error_reporting = numpy.geterr()
    numpy.seterr(invalid='ignore')     # suppress messages

    if centroid is not None:
        ar_centroid = centroid
    else:
        # simple sum since AR are equi-spaced
        numerator = numpy.ma.masked_invalid(ratio*ar)
        denominator = numpy.ma.masked_array(data=ratio, mask=numerator.mask)
        ar_centroid = numpy.sum(numerator) / numpy.sum(denominator)


    binMax = numpy.argmax(ratio)
    arMax = ar[binMax]
    rMax = ratio[binMax]
    # narrow the range of values to search (avoids unmasked spikes)
    SEARCH_PRECISION = 0.8e-4
    bins = numpy.where( numpy.abs(ar-ar_centroid) < SEARCH_PRECISION )
    y = ratio[bins]
    x = ar[bins]
    rMax = numpy.max(y)
    
    ar_fwhm = FWHM(ar, ratio)

    wavelength = get_data(hdf, '/entry/instrument/monochromator/DCM_wavelength')
    d2r = math.pi/180
    q = (4 * math.pi / wavelength) * numpy.sin(d2r*(ar_centroid - ar))

    numpy.seterr(**numpy_error_reporting)
    return dict(Q=q, centroid=ar_centroid, Rmax=rMax, FWHM=ar_fwhm)


def estimate_linear_fit_intercept(xx, yy):
    '''fit a line to xx and yy, and return the intercept and deviation'''
    def add(pair):
        x, y = pair
        src.Add(x, y)
    from StatsReg import StatsRegClass
    src = StatsRegClass()
    map(add, zip(xx, yy))
    y_mean = math.exp(src.LinearRegression()[0])
    # the error estimation is not great, yet
    #y_dev = numpy.std(yy)                           # straightforward, can we do better?
    y_sdev = src.LinearRegressionVariance()[0]      # but Y is log(), need to undo that
    y_sdev = y_mean * y_sdev                        # looks like an overestimate
    y_sdev = y_sdev / math.sqrt(float(xx.size))     # this is a guess ...
    return y_mean, y_sdev


def expand_bin_span(bin_span, bin_count, Q_diff_array, expansion_number = 2):
    '''expand the range to get enough bins for curve fitting to work properly'''
    if bin_span.size == 0:      # must have at least one bin
        bin_span = numpy.array([numpy.abs(Q_diff_array).argmin()])
    for _ in range(expansion_number):  # add more bins on each side
        bin_span = numpy.insert(bin_span, 0, bin_span.min()-1)
        bin_span = numpy.append(bin_span, bin_span.max()+1)
    # make sure bins are within range
    bin_span = bin_span[numpy.where(bin_span >= 0)]
    bin_span = bin_span[numpy.where(bin_span < bin_count)]
    return bin_span

def rebin(Q_orig, R_orig, bin_count = DEFAULT_BIN_COUNT):
    '''rebin according to the attributes, return rebinned data in dict'''
    # basic rebinning strategy
    numpy_error_reporting = numpy.geterr()
    numpy.seterr(invalid='ignore')
    
    len_full = R_orig.size
    bin_step = len_full / bin_count

    # setup a log-spaced Q bins, based on the positive Q_orig bin range
    Q_MIN = 1.1e-6
    Qmin = max(Q_MIN, numpy.min(Q_orig[numpy.where(Q_orig > 0)]))
    Qmax = numpy.max(Q_orig)
    Q = numpy.exp(numpy.linspace(math.log(Qmin), math.log(Qmax), bin_count))
    R =  numpy.zeros((bin_count), dtype='float')
    dR = numpy.zeros((bin_count), dtype='float')
    R_log = numpy.log(R_orig)

    BIN_INDEX_HALF_WIDTH = 1
    for bin in xrange(bin_count):
        bin_r = min(bin_count-1, bin+BIN_INDEX_HALF_WIDTH)
        bin_l = max(0, bin-BIN_INDEX_HALF_WIDTH)
        dq = max(abs(Q[bin_r] - Q[bin_l]), Q_MIN)
        bin_span = numpy.argwhere(numpy.abs(Q_orig-Q[bin]) < dq).flatten()
        while bin_span.size <= 4:
            # expand the range to get enough bins for curve fitting to work properly
	    bin_span = expand_bin_span(bin_span, bin_count, Q_orig-Q[bin])
        try:
            if bin_span.size > 4:
                # realistically, with bin_size expansion above, this is the only interpolator that gets used now
		x = Q_orig[bin_span] - Q[bin]
                y = R_log[bin_span]
                if False:   # error estimation is way off in this method
                    result = numpy.polyfit(x, y, 1, cov=True)
                    y_mean = math.exp(result[0][-1])
                    y_sdev = math.sqrt(abs(result[1][0][0]))      # approximate
                y_mean, y_sdev = estimate_linear_fit_intercept(x, y)          # slower but better error estimate

            elif bin_span.size > 2:
                # see: http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html
                x = Q_orig[bin_span] - Q[bin]
                y = R_log[bin_span]
                coeff = scipy.linalg.lstsq(numpy.vstack([x, numpy.ones(len(x))]).T, y)[0]
                y_mean = math.exp(coeff[-1])
                y_sdev = numpy.std(y)

            elif bin_span.size > 1:
                y = R_orig[bin_span]
                y_mean = numpy.mean(y)
                y_sdev = numpy.std(y)

            elif bin_span.size == 1:
                y_mean = R_orig[bin_span[0]]
                y_sdev = 0                          # cannot estimate

            else:
                raise ValueError, 'no data in rebinning interval'
        except (OverflowError, ValueError):
            pass
        R[bin] = y_mean
        dR[bin] = y_sdev        # FIXME: this is garbage now
    
    numpy.seterr(**numpy_error_reporting)
    
    return dict(Q=Q, R=R, dR=dR)


def h5_openGroup(parent, name, nx_class):
    '''open or create the NeXus/HDF5 group, return the object
    
    note: this should be moved to eznx!
    '''
    try:
        group = parent[name]
    except KeyError:
        group = eznx.makeGroup(parent, name, nx_class)
    return group


def h5_write_dataset(parent, name, data, **attr):
    '''write to the NeXus/HDF5 dataset, create it if necessary, return the object
    
    note: this should be moved to eznx!
    '''
    try:
        dset = parent[name]
        dset[:] = data
        eznx.addAttributes(dset, **attr)
    except KeyError:
        dset = eznx.makeDataset(parent, name, data, **attr)
    return dset


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


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

    The ratio intensity, :math:`R`, is calculated as the ratio of the two corrected count rates:

    .. math:: R[i] = A[r[i]] * { D[i] - B[r[i]] ) \over  M[i] }

    .. caution:: This all assumes that the monitor has a fixed amplifier gain (an assumption that may be changed).

    Data from the HDF5 file
    =======================

    =====================  ======================================================  ===========================================================
    term		   HDF address path					   description
    =====================  ======================================================  ===========================================================
    :math:`n`		   /entry/flyScan/AR_pulses				   number of data points in MCA arrays
    :math:`p_t` 	   /entry/flyScan/mca1  				   array of clock pulses
    :math:`p_m` 	   /entry/flyScan/mca2  				   array of monitor pulses
    :math:`p_d` 	   /entry/flyScan/mca3  				   array of detector pulses
    :math:`f_{clock}`	   /entry/flyScan/mca_clock_frequency			   MCA clock frequency
    :math:`AR_{start}`     /entry/flyScan/AR_start				   AR starting position
    :math:`\Delta E_{ar}`  /entry/flyScan/AR_increment  			   AR channel increment
    changes_mcsChan	   /entry/flyScan/changes_mcsChan			   array of MCS channels for range change events
    changes_ampGain	   /entry/flyScan/changes_ampGain			   array of detector range change events (provides :math:`r`)
    changes_ampReqGain     /entry/flyScan/changes_ampReqGain			   array of requested detector range change events
    :math:`A[0]`	   /entry/metadata/upd_gain0				   detector amplifier gain for range 0
    :math:`A[1]`	   /entry/metadata/upd_gain1				   detector amplifier gain for range 1
    :math:`A[2]`	   /entry/metadata/upd_gain2				   detector amplifier gain for range 2
    :math:`A[3]`	   /entry/metadata/upd_gain3				   detector amplifier gain for range 3
    :math:`A[4]`	   /entry/metadata/upd_gain4				   detector amplifier gain for range 4
    :math:`B[0]`	   /entry/metadata/upd_bkg0				   detector amplifier background count rate for range 0
    :math:`B[1]`	   /entry/metadata/upd_bkg1				   detector amplifier background count rate for range 1
    :math:`B[2]`	   /entry/metadata/upd_bkg2				   detector amplifier background count rate for range 2
    :math:`B[3]`	   /entry/metadata/upd_bkg3				   detector amplifier background count rate for range 3
    :math:`B[4]`	   /entry/metadata/upd_bkg4				   detector amplifier background count rate for range 4
    =====================  ======================================================  ===========================================================
    '''
    
    def __init__(self, hdf_file_name, bin_count = DEFAULT_BIN_COUNT):
        self.bin_count = bin_count
        self.full = None
        self.reduced = None
        
        if not os.path.exists(hdf_file_name):
            self.hdf_file_name = None
            raise IOError, 'file not found: ' + hdf_file_name
        self.hdf_file_name = hdf_file_name
        self.read()
    
    def read(self):
        hdf = h5py.File(self.hdf_file_name, 'r')
        
        raw_clock_pulses = get_data(hdf, '/entry/flyScan/mca1')
        raw_I0 =           get_data(hdf, '/entry/flyScan/mca2')
        raw_upd =          get_data(hdf, '/entry/flyScan/mca3')
        raw_num_points =   get_data(hdf, '/entry/flyScan/AR_pulses')
        
        AR_start =     get_data(hdf, '/entry/flyScan/AR_start')
        AR_increment = get_data(hdf, '/entry/flyScan/AR_increment')
        ar_last = AR_start - (raw_num_points - 1) * AR_increment
        raw_ar = numpy.linspace(AR_start, ar_last, raw_num_points)
        
        pulse_frequency = get_data(hdf, '/entry/flyScan/mca_clock_frequency') or  MCA_CLOCK_FREQUENCY
        channel_time_s = raw_clock_pulses / pulse_frequency
        
        gain, bkg = get_gains_bkg(hdf, raw_num_points, channel_time_s)
        
        ratio = (raw_upd - bkg) / raw_I0 / gain
        ratio = numpy.ma.masked_invalid(ratio)
        ratio = numpy.ma.masked_less_equal(ratio, 0)
        
        R = ratio.compressed()
        AR = numpy.ma.masked_array(data=raw_ar, mask=ratio.mask).compressed()
        
        peak_stats = compute_Q_centroid_and_Rmax(hdf, AR, R)
        Q = peak_stats['Q']
        
        self.full = dict(AR=AR, R=R, **peak_stats)
        
        hdf.close()   # be CERTAIN to close the file
    
    def rebin(self, bin_count = None):
        '''generate R(Q) with a specified number of bins'''
        bin_count = bin_count or self.bin_count
        self.reduced = rebin(self.full['Q'], self.full['R'], bin_count)
    
    def save(self, hdf_file_name = None, save_full = True, save_rebinned = True):
        '''
	save the data to an HDF5 file, return filename or None if not written
	
	By default, save to the input HDF5 file.
	To override this, specify the output HDF5 file name when calling this method.
	
	* If the file exists, this will not overwrite any input data.
	* Set *save_full* to *False* to suppress writing the full, reduced :math:`R(Q)`
	* Full, reduced :math:`R(Q)` goes into NXdata group::
	
	    /entry/flyScan_reduced_full
	
	* a previous full reduced :math:`R(Q)` will be replaced.

	* It may replace the rebinned, reduced :math:`R(Q)` 
	  if a NXdata group of the same number of bins exists.
	* Rebinned, reduced :math:`R(Q)`  goes into NXdata group::
	  
	      /entry/flyScan_reduced_<N>
	
	  where ``<N>`` is the bins, such as (for 500 bins):: 
	  
	      /entry/flyScan_reduced_500
	
	* Set *save_rebinned* to *False* to suppress writing the rebinned, reduced :math:`R(Q)` 
	
	:see: http://download.nexusformat.org/doc/html/classes/base_classes/NXentry.html
	:see: http://download.nexusformat.org/doc/html/classes/base_classes/NXdata.html
	'''
        if hdf_file_name is not None:
            if not os.path.exists(hdf_file_name):
                hdf_file_name = self.hdf_file_name
        else:
            hdf_file_name = self.hdf_file_name
                
        if self.full is None and self.reduced is None:
            return None

        hdf = h5py.File(hdf_file_name, 'a')
        
        nxentry = h5_openGroup(hdf, 'entry', 'NXentry')
	# TODO: consider adding something to describe the sample
	# Problem is when multiple of these files are opened in PyMca, NeXpy, IgorPro,
	#  the datasets all have the same (or similar) NXdata group names 
	#  and identical dataset names.  Those tools have a tough time differentiating.
	# Possibly, full R(W) goes into a new group with the NXdata including the file name.  Something.
	# Similar for rebinned.  Make that change soon **before** we make a lot of files!

        if self.full is not None:
            nxdata = h5_openGroup(nxentry, 'flyScan_reduced_full', 'NXdata')
	    # TODO: add timestamp to this group as attribute
            h5_write_dataset(nxdata, "AR",          self.full['AR'],       units='degrees')
            h5_write_dataset(nxdata, "Q",           self.full['Q'],        units='1/A')
            h5_write_dataset(nxdata, "R",           self.full['R'],        units='a.u.', signal=1, axes='Q')
            h5_write_dataset(nxdata, "R_max",       [self.full['Rmax']],     units='a.u.')
            h5_write_dataset(nxdata, "AR_centroid", [self.full['centroid']], units='degrees')
            h5_write_dataset(nxdata, "AR_FWHM",     [self.full['FWHM']],     units='degrees')
        
        if self.reduced is not None:
	    # TODO: add timestamp to this group as attribute
            nxdata =  h5_openGroup(nxentry, 'flyScan_reduced_'+str(self.reduced['Q'].size), 'NXdata')
            h5_write_dataset(nxdata, "Q",  self.reduced['Q'],  units='1/A')
            h5_write_dataset(nxdata, "R",  self.reduced['R'],  units='a.u.', signal=1, axes='Q', uncertainty='dR')
            h5_write_dataset(nxdata, "dR", self.reduced['dR'], units='a.u.')
        
        hdf.close()   # be CERTAIN to close the file
        return hdf_file_name


def main():
    '''standard command-line interface'''
    import argparse
    parser = argparse.ArgumentParser(prog='reduceFlyData', description=__doc__)
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

    cmd_args = parser.parse_args()

    print "Reducing data in " + cmd_args.hdf5_file
    scan = UsaxsFlyScan(cmd_args.hdf5_file, bin_count=cmd_args.num_bins)
    print '  rebinning'
    scan.rebin()
    if len(cmd_args.hdf5_file) > 0:
        output_filename = cmd_args.hdf5_file
        msg = '  saving to '
    else:
        output_filename = None
        msg = '  saving back to '
    print msg + scan.save(output_filename)


if __name__ == '__main__':
    #developer_test()
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
