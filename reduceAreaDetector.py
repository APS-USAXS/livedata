#!/usr/bin/env python

'''reduceAreaDetector: reduce the raw data from Area Detector images to R(Q)'''

import h5py                 #@UnusedImport
import logging
import math                 #@UnusedImport
import numpy                #@UnusedImport
import os                   #@UnusedImport
# import scipy.interpolate    #@UnusedImport
# import shutil               #@UnusedImport
# import stat                 #@UnusedImport
import warnings

from spec2nexus import eznx #@UnusedImport
import calc
import localConfig          #@UnusedImport
import pvwatch
# import ustep                #@UnusedImport
from radialprofile import azimuthalAverage

logger = logging.getLogger(__name__)

# TODO: list
# [x] copy fly scan data reduction code for SAXS&WAXS
# [x] identify good set of test data (from Feb 2016)
# [x] integrate canned routine into reduction code
# [x] create developer code to test reduction code
# [x] write results to temporary HDF5 file
# [~] resolve problem with wrong-looking std dev calc
# [ ] construct and apply image mask
# [x] refactor developer code for regular use
# [x] write results back to original HDF5 file
# [x] integrate with routine data reduction code
# [x] plot on livedata page
# [x] resolve problem with h5py, cannot append reduced data to existing file


DEFAULT_BIN_COUNT   = localConfig.REDUCED_AD_IMAGE_BINS
PIXEL_SIZE_TOLERANCE = 1.0e-6
ESD_FACTOR          = 0.01      # estimate dr = ESD_FACTOR * r  if r.std() = 0 : 1% errors

# define the locations of the source data in the HDF5 file
# there are various possible layouts
AD_HDF5_ADDRESS_MAP = {
    'local_name'            : '/entry/data/local_name',
    'Pilatus 100K' : {
        'image'                 : '/entry/data/data',
        'wavelength'            : '/entry/Metadata/wavelength',
        'SDD'                   : '/entry/Metadata/SDD',
        # image is transposed, consider that here
        'y_image_center_pixels' : '/entry/instrument/detector/beam_center_x',
        'x_image_center_pixels' : '/entry/instrument/detector/beam_center_y',
        'x_pixel_size_mm'       : '/entry/instrument/detector/x_pixel_size',
        'y_pixel_size_mm'       : '/entry/instrument/detector/y_pixel_size',
        'I0_counts'             : '/entry/Metadata/I0_cts_gated',
        'I0_gain'               : '/entry/Metadata/I0_gain',
        # need to consider a detector-dependent mask
    },
    'Pilatus 300Kw' : {
        'image'                 : '/entry/data/data',
        'wavelength'            : '/entry/Metadata/dcm_wavelength',
        # TODO: Now? 'wavelength'            : '/entry/Metadata/wavelength',
        'SDD'                   : '/entry/Metadata/SDD',
        # image is transposed, consider that here
        'y_image_center_pixels' : '/entry/instrument/detector/beam_center_x',
        'x_image_center_pixels' : '/entry/instrument/detector/beam_center_y',
        'x_pixel_size_mm'       : '/entry/instrument/detector/x_pixel_size',
        'y_pixel_size_mm'       : '/entry/instrument/detector/y_pixel_size',
        'I0_counts'             : '/entry/Metadata/I0_cts_gated',
        'I0_gain'               : '/entry/Metadata/I0_gain',
        # need to consider a detector-dependent mask
    },
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class AD_ScatteringImage(object):

    def __init__(self, hdf5_file_name):
        if not os.path.exists(hdf5_file_name):
            raise IOError, 'file not found: ' + hdf5_file_name
        self.hdf5_file_name = hdf5_file_name
        self.image = None
        self.reduced = {}

        self.units = dict(
            x = 'mm',
            Q = '1/A',
            R = 'none',
            dR = 'none',
        )

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

    def reduce(self):
        '''convert raw image data to R(Q), also get other terms'''
        if self.image is None:      # TODO: make this conditional on need to reduce image data
            self.read_image_data()

        if abs(self.image.xsize - self.image.ysize) > PIXEL_SIZE_TOLERANCE:
            raise ValueError('X & Y pixels have different sizes, not prepared for this')

        # TODO: construct the image mask

        # radial averaging (average around the azimuth at constant radius, repeat at all radii)
        with numpy.errstate(invalid='ignore'):
            radii, rAvg = azimuthalAverage(self.image.image,
                                           center=(self.image.x0, self.image.y0),
                                           returnradii=True)

        # standard deviation results do not look right, skip that in full data reduction
        # with numpy.errstate(invalid='ignore'):
        #     with warnings.catch_warnings():
        #         # sift out this RuntimeWarning warning from numpy
        #         warnings.filterwarnings('ignore', r'Degrees of freedom <= 0 for slice')
        #         rAvgDev = azimuthalAverage(self.image.image,
        #                                        center=(self.image.x0, self.image.y0),
        #                                        stddev=True)

        radii *= self.image.xsize
        Q = (4*math.pi / self.image.wavelength) * numpy.sin(0.5*numpy.arctan2(radii, self.image.SDD))
        # scale_factor = 1 /self.image.I0_gain / self.image.I0     # TODO: verify the equation
        scale_factor = 1 / self.image.I0     # TODO: verify the equation
        rAvg = rAvg * scale_factor

        # remove NaNs and non-positives from output data
        rAvg = numpy.ma.masked_less_equal(rAvg, 0)  # mask the non-positives
        rAvg = numpy.ma.masked_invalid(rAvg)        # mask the NaNs
        Q = calc.remove_masked_data(Q, rAvg.mask)
        radii = calc.remove_masked_data(radii, rAvg.mask)
        # rAvgDev = calc.remove_masked_data(rAvgDev, rAvg.mask)
        rAvg = calc.remove_masked_data(rAvg, rAvg.mask)     # always remove the masked array last

        full = dict(Q=Q, R=rAvg, x=radii)
        self.reduced = dict(full = full)    # reset the entire dictionary with new "full" reduction

    def rebin(self, bin_count=250):
        '''
        generate R(Q) with a bin_count bins

        save in ``self.reduced[str(bin_count)]`` dict
        '''
        if not self.has_reduced():
            self.reduce()
            if 'full' not in self.reduced:
                raise IndexError('no data reduction: ' + self.hdf5_file_name)
                #return

        bin_count_full = len(self.reduced['full']['Q'])
        bin_count = min(bin_count, bin_count_full)
        s = str(bin_count)

        Q_full = self.reduced['full']['Q']
        R_full = self.reduced['full']['R']

        # lowest non-zero Q value > 0 or minimum acceptable Q
        Qmin = Q_full.min()
        Qmax = 1.0001 * Q_full.max()

        # pick the Q binning
        Q_bins = numpy.linspace(Qmin, Qmax, bin_count)

        qVec, rVec, drVec = [], [], []
        for xref in calc.bin_xref(Q_full, Q_bins):
            if len(xref) > 0:
                q = Q_full[xref]
                r = R_full[xref]
                # average Q & R in log-log space, won't matter to WAXS data at higher Q
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
          'full': dict(Q, R)
          '250':  dict(Q, R, dR)
          '50':   dict(Q, R, dR)
        }
        '''
        fields = self.units.keys()
        reduced = {}
        hdf = h5py.File(self.hdf5_file_name, 'r')
        entry = hdf['/entry']
        for key in entry.keys():
            if key.startswith('areaDetector_reduced_'):
                nxdata = entry[key]
                nxname = key[len('areaDetector_reduced_'):]
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

            /entry/areaDetector_reduced_full

        * any previous full reduced :math:`R(Q)` will be replaced.

        * It may replace the rebinned, reduced :math:`R(Q)`
          if a NXdata group of the same number of bins exists.
        * Rebinned, reduced :math:`R(Q)`  goes into NXdata group::

              /entry/areaDetector_reduced_<N>

          where ``<N>`` is the number of bins, such as (for 500 bins)::

              /entry/areaDetector_reduced_500

        :see: http://download.nexusformat.org/doc/html/classes/base_classes/NXentry.html
        :see: http://download.nexusformat.org/doc/html/classes/base_classes/NXdata.html
        '''
        key = str(key)
        if key not in self.reduced:
            return
        nxname = 'areaDetector_reduced_' + key
        hfile = hfile or self.hdf5_file_name
        ds = self.reduced[key]
        try:
            hdf = h5py.File(hfile, 'a')
        except IOError, _exc:
            # FIXME: some h5py problem in <h5py>/_hl/files.py, line 101
            # this fails: fid = h5f.open(name, h5f.ACC_RDWR, fapl=fapl)
            # with IOError that is improperly caught on next and then:
            # fid = h5f.create(name, h5f.ACC_EXCL, fapl=fapl, fcpl=fcpl) fails with IOError
            # since the second call has "name" with all lower case
            #
            # real problem is that these HDF5 files have the wrong uid/gid, as set by the Pilatus computer
            # TODO: fix each Pilatus and this problem will go away
            # TODO: change uid/gid on all the acquired HDF5 files (*.h5, *.hdf) under usaxscontrol:/share1/USAXS_data/2*
            # Files should be owned by usaxs:usaxs (1810:2026), but are owned by tomo2:usaxs (500:2026) as seen by usaxs@usaxscontrol
            # not enough to change the "umask" on the det@dec1122 computer, what else will fix this?
            pvwatch.logMessage( "Problem writing reduced data back to file: " + hfile )
            return
        if 'default' not in hdf.attrs:
            hdf.attrs['default'] = 'entry'
        nxentry = eznx.openGroup(hdf, 'entry', 'NXentry')
        if 'default' not in nxentry.attrs:
            nxentry.attrs['default'] = nxname
        nxdata = eznx.openGroup(nxentry,
                                nxname,
                                'NXdata',
                                signal='R',
                                axes='Q',
                                Q_indices=0,
                                timestamp=calc.iso8601_datetime(),
                                )
        for key in sorted(ds.keys()):
            try:
                _ds = eznx.write_dataset(nxdata, key, ds[key])
                if key in self.units:
                    eznx.addAttributes(_ds, units=self.units[key])
            except RuntimeError, e:
                pass        # TODO: reporting
        hdf.close()
        return hfile


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

        determine if SAXS or WAXS based on detector name as coded into the h5addr
        '''
        detector_name_h5addr = AD_HDF5_ADDRESS_MAP['local_name']
        detector_name = str(self.fp[detector_name_h5addr].value[0])
        self.hdf5_addr_map = h5addr = AD_HDF5_ADDRESS_MAP[detector_name]
        self.filename    = self.fp.filename
        self.image       = numpy.array(self.fp[h5addr['image']])
        self.wavelength  = self.fp[h5addr['wavelength']][0]
        self.SDD         = self.fp[h5addr['SDD']][0]
        self.x0          = self.fp[h5addr['x_image_center_pixels']][0]
        self.y0          = self.fp[h5addr['y_image_center_pixels']][0]
        self.xsize       = self.fp[h5addr['x_pixel_size_mm']][0]
        self.ysize       = self.fp[h5addr['y_pixel_size_mm']][0]
        self.I0          = self.fp[h5addr['I0_counts']][0]
        self.I0_gain     = self.fp[h5addr['I0_gain']][0]
        # later, scale each image by metadata I0_cts_gated and I0_gain
        # TODO: get image mask specifications
        return


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


def reduce_area_detector_data(hdf5_file,
                              num_bins,
                              recompute_full=False,
                              recompute_rebinned=False,
                              output_filename=None):
    '''
    reduce areaDetector image data to R(Q)

    :param str hdf5_file: name of HDF5 file with AD image data
    :param int num_bins: number of bins in rebinned data set
    :param bool recompute_full: set True to force recompute,
           even if reduced data already in data file (default: False)
    :param bool recompute_rebinned: set True to force recompute,
           even if reduced data already in data file (default: False)
    :param str output_filename: name of file to write reduced data
           if None, use hdf5_file (default: None)
    '''
    needs_calc = {}
    pvwatch.logMessage( "Area Detector data file: " + hdf5_file )
    scan = AD_ScatteringImage(hdf5_file)   # initialize the object

    s_num_bins = str(num_bins)
    output_filename = output_filename or hdf5_file

    pvwatch.logMessage( '  checking for previously-saved R(Q)' )
    scan.read_reduced()

    needs_calc['full'] = not scan.has_reduced('full')
    if recompute_full:
        needs_calc['full'] = True
    needs_calc[s_num_bins] = not scan.has_reduced(s_num_bins)
    if recompute_rebinned:
        needs_calc[s_num_bins] = True

    if needs_calc['full']:
        pvwatch.logMessage('  reducing Area Detector image to R(Q)')
        scan.reduce()
        pvwatch.logMessage( '  saving reduced R(Q) to ' + output_filename)
        scan.save(hdf5_file, 'full')
        needs_calc[s_num_bins] = True

    if needs_calc[s_num_bins]:
        msg = '  rebinning R(Q) (from %d) to %d points'
        msg = msg % (scan.reduced['full']['Q'].size, num_bins)
        pvwatch.logMessage( msg )
        scan.rebin(num_bins)
        pvwatch.logMessage( '  saving rebinned R(Q) to ' + output_filename )
        scan.save(hdf5_file, s_num_bins)

    return scan


def command_line_interface():
    '''standard command-line interface'''
    cmd_args = get_user_options()

    if len(cmd_args.output_file) > 0:
        output_filename = cmd_args.output_file
    else:
        output_filename = cmd_args.hdf5_file

    scan = reduce_area_detector_data(cmd_args.hdf5_file,
                              cmd_args.num_bins,
                              recompute_full=cmd_args.recompute_full,
                              recompute_rebinned=cmd_args.recompute_rebinned,
                              output_filename=output_filename)
    return scan


if __name__ == '__main__':
    if False:
        # for developer use only
        import sys
        # sys.argv.append("/share1/USAXS_data/2018-01/01_30_Settle_waxs/Adam_0184.hdf")
        sys.argv.append("/tmp/Adam_0184.hdf")
    command_line_interface()
