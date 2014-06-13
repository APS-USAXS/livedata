#!/usr/bin/env python

'''
handle 2-D raw SAXS and WAXS data
'''


import os
import h5py
import numpy
import matplotlib.pyplot as plt

TEST_FILE = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'waxs', 'LSM_YSZ_infl_227.hdf5')
HDF5_DATA_PATH = '/entry/data/data'
SCALING_FACTOR = 1        #  2**24
PLOT_H_INT = 7
PLOT_V_INT = 3
COLORMAP = 'cubehelix'        # http://matplotlib.org/api/pyplot_summary.html#matplotlib.pyplot.colormaps
PNG_FILE = 'image.png'


def make_png(h5file, pngfile, h5path=HDF5_DATA_PATH, hsize=PLOT_H_INT, vsize=PLOT_V_INT, cmap=COLORMAP):
    if not os.path.exists(h5file):
        msg = 'file does not exist: ' + h5file
        raise IOError, msg

    hdf5 = h5py.File(h5file)
    ds = hdf5[h5path]
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
