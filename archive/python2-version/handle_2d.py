#!/usr/bin/env python

'''
handle 2-D raw SAXS and WAXS data
'''


import os
import h5py
import logging
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)

PATH_TO_HERE = os.path.abspath(os.path.split(__file__)[0])
TEST_FILE = os.path.join(PATH_TO_HERE, 'testdata', '2014-06-12', 'waxs', 'LSM_YSZ_infl_227.hdf5')
HDF5_DATA_PATH = '/entry/data/data'
SCALING_FACTOR = 1        #  2**24
PLOT_H_INT = 7
PLOT_V_INT = 3
COLORMAP = 'cubehelix'        # http://matplotlib.org/api/pyplot_summary.html#matplotlib.pyplot.colormaps
IMG_FILE = os.path.join(PATH_TO_HERE, 'image.png')

# MatPlotLib advises to re-use the figure() object rather create new ones
# http://stackoverflow.com/questions/21884271/warning-about-too-many-open-figures
MPL_FIG = None


def make_png(h5file, imgfile, h5path=HDF5_DATA_PATH, log_image=True,
             hsize=PLOT_H_INT, vsize=PLOT_V_INT, cmap=COLORMAP):
    '''
    read the image from the named HDF5 file and make a PNG file

    Test that the HDF5 file exists and that the path to the data exists in that file.
    Read the data from the named dataset, mask off some bad values,
    convert to log(image) and use Matplotlib to make the PNG file.

    The HDF5 file could be a NeXus file, not required though.

    :param str h5file: name of HDF5 file (path is optional)
    :param str imgfile: name of image file to be written (path is optional)
    :param str h5path: path to the image dataset within the HDF5 file
       (default = '/entry/data/data', common for some NeXus data files)
    :param bool log_image: plot log(image)
    :param int hsize: horizontal size of the PNG image (default: 7)
    :param int hsize: vertical size of the PNG image (default: 3)
    :param str cmap: colormap for the image (default: 'cubehelix'), 'jet' is another good one
    :return str: *imgfile*
    :raises: IOError if either *h5file* or *h5path* are not found
    '''
    global MPL_FIG
    if not os.path.exists(h5file):
        raise IOError('file does not exist: ' + h5file)

    with h5py.File(h5file, 'r') as hdf5:
        try:
            ds = hdf5[h5path]
        except:
            msg = 'h5path not found in HDF5 file:'
            msg += '\n  file: ' + h5file
            msg += '\n  path: ' + h5path
            raise IOError(msg)

        image_data = numpy.ma.masked_less_equal(ds.value, 0)
        # replace masked data with min good value
        image_data = image_data.filled(image_data.min())

        if log_image and image_data.max() != 0:
            image_data = numpy.log(image_data)
            image_data -= image_data.min()
            image_data *= SCALING_FACTOR / image_data.max()

    plt.set_cmap(cmap)
    if MPL_FIG is None:
        MPL_FIG = plt.figure(figsize=(hsize, vsize))
    else:
        MPL_FIG.clf()
    ax = MPL_FIG.add_subplot(111)
    ax.cla()
    ax.set_title(h5file, fontsize=9)
    ax.imshow(image_data, interpolation='nearest')
    MPL_FIG.savefig(imgfile, bbox_inches='tight')
    plt.close(MPL_FIG)
    return imgfile


if __name__ == '__main__':
    make_png(TEST_FILE, IMG_FILE)
