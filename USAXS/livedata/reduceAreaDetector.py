#!/usr/bin/env python

'''reduceAreaDetector: reduce the raw data from Area Detector images to R(Q)'''

import datetime             #@UnusedImport
import h5py                 #@UnusedImport
import math                 #@UnusedImport
import numpy                #@UnusedImport
import os                   #@UnusedImport
# import scipy.interpolate    #@UnusedImport
# import shutil               #@UnusedImport
# import stat                 #@UnusedImport
import warnings

from spec2nexus import eznx #@UnusedImport
# import calc
import localConfig          #@UnusedImport
import pvwatch
# import ustep                #@UnusedImport
from radialprofile import azimuthalAverage


# TODO: list
# [x] copy fly scan data reduction code for SAXS&WAXS
# [x] identify good set of test data (from Feb 2016)
# [x] integrate canned routine into reduction code
# [x] create developer code to test reduction code
# [x] write results to temporary HDF5 file
# [~] resolve problem with wrong-looking std dev calc
# [ ] construct and apply image mask
# [ ] refactor developer code for regular use
# [ ] write results back to original HDF5 file
# [ ] integrate with routine data reduction code
# [ ] plot on livedata page


DEFAULT_BIN_COUNT   = localConfig.REDUCED_AD_IMAGE_BINS
PIXEL_SIZE_TOLERANCE = 1.0e-6

# define the locations of the source data in the HDF5 file
# there are various possible layouts
AD_HDF5_PINSAXS_MAP = {
    'local_name_match'      : 'Pilatus 100K',
    'local_name'            : '/entry/data/local_name',
    'image'                 : '/entry/data/data',
    'wavelength'            : '/entry/EPICS_PV_metadata/wavelength',
    'SDD'                   : '/entry/EPICS_PV_metadata/SDD',
    'SAXS_or_WAXS'          : 'SAXS',
    # image is transposed, consider that here
    'y_image_center_pixels' : '/entry/EPICS_PV_metadata/pin_ccd_center_x_pixel',
    'x_image_center_pixels' : '/entry/EPICS_PV_metadata/pin_ccd_center_y_pixel',
    'x_pixel_size_mm'       : '/entry/EPICS_PV_metadata/pin_ccd_pixel_size_x',
    'y_pixel_size_mm'       : '/entry/EPICS_PV_metadata/pin_ccd_pixel_size_y',
    'I0_counts'             : '/entry/EPICS_PV_metadata/I0_cts_gated',
    'I0_gain'               : '/entry/EPICS_PV_metadata/I0_gain',
    # need to consider a detector-dependent mask
}
AD_HDF5_WAXS_MAP = {
    'local_name_match'      : 'Pilatus 300Kw',
    'local_name'            : '/entry/data/local_name',
    'image'                 : '/entry/data/data',
    'wavelength'            : '/entry/EPICS_PV_metadata/dcm_wavelength',
    'SDD'                   : '/entry/EPICS_PV_metadata/SDD',
    'SAXS_or_WAXS'          : 'WAXS',
    # image is transposed, consider that here
    'y_image_center_pixels' : '/entry/EPICS_PV_metadata/waxs_ccd_center_x_pixel',
    'x_image_center_pixels' : '/entry/EPICS_PV_metadata/waxs_ccd_center_y_pixel',
    'x_pixel_size_mm'       : '/entry/EPICS_PV_metadata/waxs_ccd_pixel_size_x',
    'y_pixel_size_mm'       : '/entry/EPICS_PV_metadata/waxs_ccd_pixel_size_y',
    'I0_counts'             : '/entry/EPICS_PV_metadata/I0_cts_gated',
    'I0_gain'               : '/entry/EPICS_PV_metadata/I0_gain',
    # need to consider a detector-dependent mask
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class Reduce(object):
    
    def __init__(self, hdf5_file_name):
        if not os.path.exists(hdf5_file_name):
            raise IOError, 'file not found: ' + hdf5_file_name
        self.hdf5_file_name = hdf5_file_name
        self.image = None
        self.reduced = {}
        
    def read_image_data(self):
        '''
        read image data from the HDF5 file, return as instance of :class:`Image`
        '''
        fp = h5py.File(self.hdf5_file_name)
        self.image = Image(fp)
        self.image.read_image_data()
        fp.close()
        return self.image
        
    def has_reduced(self, key = 'full'):
        '''
        check if the reduced dataset is available
        
        :param str|int key: name of reduced dataset (default = 'full')
        '''
        key = str(key)
        if key not in self.reduced:
            return False
        return 'Q' in self.reduced[key] and 'R' in self.reduced[key]
        
    def read_reduced(self):
        '''
        read any and all reduced data from the HDF5 file, return in a dictionary
        
        dictionary = {
          'full': dict(Q, R, R_max, ar, fwhm, centroid)
          '250':  dict(Q, R, dR)
          '5000': dict(Q, R, dR)
        }
        '''
        if self.image is None:      # TODO: make this conditional on need to reduce image data
            self.read_image_data()

        developer(self.image)   # TODO: refactor this into "full" data reduction


def get_user_options():
    '''parse the command line for the user options'''
    import argparse
    parser = argparse.ArgumentParser(prog='reduceAreaDetector', description=__doc__)
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
    pvwatch.logMessage( "Area Detector data file: " + cmd_args.hdf5_file )
    scan = Reduce(cmd_args.hdf5_file)   # initialize the object

    pvwatch.logMessage( '  checking for previously-saved R(Q)' )
    scan.read_reduced()
    needs_calc['full'] = not scan.has_reduced('full')   # TODO: needs method scan.has_reduced()
    if cmd_args.recompute_full:
        needs_calc['full'] = True
    needs_calc[s_num_bins] = not scan.has_reduced(s_num_bins)
    if cmd_args.recompute_rebinned:
        needs_calc[s_num_bins] = True
    needs_calc['250'] = True    # FIXME: developer only

    if needs_calc['full']:
        pvwatch.logMessage('  reducing Area Detector image to R(Q)')
        scan.reduce()
        pvwatch.logMessage( '  saving reduced R(Q) to ' + output_filename)
        scan.save(cmd_args.hdf5_file, 'full')
        needs_calc[s_num_bins] = True
    if needs_calc[s_num_bins]:
        pvwatch.logMessage( '  rebinning R(Q) (from %d) to %d points' % (scan.reduced['full']['Q'].size, cmd_args.num_bins) )
        scan.rebin(cmd_args.num_bins)
        pvwatch.logMessage( '  saving rebinned R(Q) to ' + output_filename )
        scan.save(cmd_args.hdf5_file, s_num_bins)
    return scan


class Image(object):
    
    def __init__(self, fp):
        self.fp = fp

        self.filename       = None
        self.image          = None
        self.wavelength     = None
        self.SDD            = None
        self.x0             = None
        self.y0             = None
        self.xsize          = None
        self.ysize          = None
        self.I0             = None
        self.I0_gain        = None
        self.hdf5_addr_map  = None
    
    def read_image_data(self):
        '''
        get the image from the HDF5 file
        
        determine if SAXS or WAXS based on detector name as coded into the hdf5_map
        '''
        for hdf5_map in (AD_HDF5_PINSAXS_MAP, AD_HDF5_WAXS_MAP):
            detector_name = self.fp.get(hdf5_map['local_name'], None)[0]
            if detector_name == hdf5_map['local_name_match']:
                self.hdf5_addr_map = hdf5_map
                self.filename    = self.fp.filename
                self.image       = numpy.array(self.fp[hdf5_map['image']])
                self.wavelength  = self.fp[hdf5_map['wavelength']][0]
                self.SDD         = self.fp[hdf5_map['SDD']][0]
                self.x0          = self.fp[hdf5_map['x_image_center_pixels']][0]
                self.y0          = self.fp[hdf5_map['y_image_center_pixels']][0]
                self.xsize       = self.fp[hdf5_map['x_pixel_size_mm']][0]
                self.ysize       = self.fp[hdf5_map['y_pixel_size_mm']][0]
                self.I0          = self.fp[hdf5_map['I0_counts']][0]
                self.I0_gain     = self.fp[hdf5_map['I0_gain']][0]
                # later, scale each image by metadata I0_cts_gated and I0_gain
                # TODO: get image mask specifications
                return
            

def developer(hdf5, output_filename=None):  # TODO: refactor this into "full" data reduction
    '''
    data reduction: development version
    
    :param obj hdf5: instance of :class:`Image`
    '''
    if hdf5 is None:
        return
    if abs(hdf5.xsize - hdf5.ysize) > PIXEL_SIZE_TOLERANCE:
        raise ValueError('X & Y pixels have different sizes, not prepared for this')
    
    # TODO: construct the image mask
    
    with numpy.errstate(invalid='ignore'):
        radii, rAvg = azimuthalAverage(hdf5.image, 
                                       center=(hdf5.x0, hdf5.y0), 
                                       returnradii=True)
    # with numpy.errstate(invalid='ignore'):
    #     with warnings.catch_warnings():
    #         # sift out this RuntimeWarning warning from numpy
    #         warnings.filterwarnings('ignore', r'Degrees of freedom <= 0 for slice')
    #         rAvgDev = azimuthalAverage(hdf5.image, 
    #                                        center=(hdf5.x0, hdf5.y0), 
    #                                        stddev=True)

    radii *= hdf5.xsize
    Q = (4*math.pi / hdf5.wavelength) * numpy.sin(0.5*numpy.arctan2(radii, hdf5.SDD))
    scale_factor = hdf5.I0_gain / hdf5.I0     # TODO: verify the equation
    rAvg = rAvg * scale_factor
    # rAvgDev = rAvgDev * scale_factor        # TODO: Find out why rAvgDev > rAvg
    # TODO: remove NaNs from output data
    
    if output_filename is None:
        path = os.path.dirname(hdf5.filename)
        output_filename = os.path.join(path, 'testfile.hdf5')

    fp = eznx.makeFile(output_filename, default='entry')

    nxentry = eznx.makeGroup(fp, 'entry', 'NXentry', default='reduced_full')
    eznx.makeDataset(nxentry, 'title', hdf5.filename)

    nxdata = eznx.makeGroup(nxentry, 'reduced_full', 'NXdata', 
                            signal='R', axes='Q', Q_indices=[0,])

    eznx.makeDataset(nxdata, 'x', radii, units='mm',
                          long_name='distance from beam center, mm')
    eznx.makeDataset(nxdata, 'Q', Q, units='1/A',
                          long_name='|Q|, 1/A')
    eznx.makeDataset(nxdata, 'R', rAvg, units='counts',
                          long_name='radially-averaged data')
    # eznx.makeDataset(nxdata, 'Rdev', rAvgDev, units='counts',
    #                       long_name='standard deviation of radially-averaged data')
    fp.close()


if __name__ == '__main__':
    #command_line_interface()
    pass    # TODO: remove for production use


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

