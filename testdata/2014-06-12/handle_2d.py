#!/usr/bin/env python

'''
handle 2-D raw SAXS and WAXS data
'''


import os
import h5py
import numpy
import matplotlib.pyplot as plt


PATH_TO_HERE = os.path.abspath(os.path.split(__file__)[0])
TEST_FILE = os.path.join(PATH_TO_HERE, 'waxs', 'LSM_YSZ_infl_227.hdf5')
HDF5_DATA_PATH = '/entry/data/data'
SCALING_FACTOR = 1        #  2**24
PLOT_H_INT = 7
PLOT_V_INT = 3
COLORMAP = 'cubehelix'        # http://matplotlib.org/api/pyplot_summary.html#matplotlib.pyplot.colormaps
PNG_FILE = 'image.png'


def make_png(h5file, pngfile, h5path=HDF5_DATA_PATH, 
             hsize=PLOT_H_INT, vsize=PLOT_V_INT, cmap=COLORMAP):
    '''
    read the image from the named HDF5 file and make a PNG file
    
    Test that the HDF5 file exists and that the path to the data exists in that file.
    Read the data from the named dataset, mask off some bad values, 
    convert to log(image) and use Matplotlib to make the PNG file.
    
    The HDF5 file could be a NeXus file, not required though.
    
    :param str h5file: name of HDF5 file (path is optional)
    :param str pngfile: name of PNG file to be written (path is optional)
    :param str h5path: path to the image dataset within the HDF5 file
       (default = '/entry/data/data', common for some NeXus data files)
    :param int hsize: horizontal size of the PNG image (default: 7)
    :param int hsize: vertical size of the PNG image (default: 3)
    :param str cmap: colormap for the image (default: 'cubehelix'), 'jet' is another good one
    :return str: *pngfile*
    :raises: IOError if either *h5file* or *h5path* are not found
    '''
    if not os.path.exists(h5file):
        msg = 'file does not exist: ' + h5file
        raise IOError, msg

    hdf5 = h5py.File(h5file)
    try:
        ds = hdf5[h5path]
    except:
        msg = 'h5path not found in HDF5 file:'
        msg += '\n  file: ' + h5file
        msg += '\n  path: ' + h5path
        raise IOError, msg

    image_data = numpy.ma.masked_less_equal(ds.value, 0)
    image_data = image_data.filled(image_data.min())    # replace masked data with min good value
    #meta = dict(hi=image_data.max(), lo=image_data.min(), h=image_data.shape[0], w=image_data.shape[1])
    log_image = numpy.log(image_data)
    log_image -= log_image.min()
    log_image *= SCALING_FACTOR / log_image.max()

    plt.set_cmap(cmap)
    fig = plt.figure(figsize=(hsize, vsize))
    ax = fig.add_subplot(111)
    ax.cla()
    ax.imshow(log_image, interpolation='nearest')
    fig.savefig(pngfile)
    return pngfile


if __name__ == '__main__':
    make_png(TEST_FILE, PNG_FILE)
