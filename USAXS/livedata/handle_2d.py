#!/usr/bin/env python

'''
handle 2-D raw SAXS and WAXS data
'''


import os
import h5py
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


PATH_TO_HERE = os.path.abspath(os.path.split(__file__)[0])
TEST_FILE = os.path.join(PATH_TO_HERE, 'testdata', '2014-06-12', 'waxs', 'LSM_YSZ_infl_227.hdf5')
HDF5_DATA_PATH = '/entry/data/data'
SCALING_FACTOR = 1        #  2**24
PLOT_H_INT = 7
PLOT_V_INT = 3
COLORMAP = 'cubehelix'        # http://matplotlib.org/api/pyplot_summary.html#matplotlib.pyplot.colormaps
IMG_FILE = 'image.png'


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
    if not os.path.exists(h5file):
        msg = 'file does not exist: ' + h5file
        raise IOError, msg

    hdf5 = h5py.File(h5file, 'r')
    try:
        ds = hdf5[h5path]
    except:
        msg = 'h5path not found in HDF5 file:'
        msg += '\n  file: ' + h5file
        msg += '\n  path: ' + h5path
        raise IOError, msg

    image_data = numpy.ma.masked_less_equal(ds.value, 0)
    # replace masked data with min good value
    image_data = image_data.filled(image_data.min())
    if log_image:
        image_data = numpy.log(image_data)
        image_data -= image_data.min()
        image_data *= SCALING_FACTOR / image_data.max()

    plt.set_cmap(cmap)
    fig = plt.figure(figsize=(hsize, vsize))
    ax = fig.add_subplot(111)
    ax.cla()
    ax.set_title(h5file, fontsize=9)
    ax.imshow(image_data, interpolation='nearest')
    fig.savefig(imgfile, bbox_inches='tight')
    plt.close(fig)
    return imgfile


if __name__ == '__main__':
    make_png(TEST_FILE, IMG_FILE)


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
