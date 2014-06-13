#!/usr/bin/env python

'''
handle 2-D raw SAXS and WAXS data
'''


import os
import h5py
import numpy
from PySide import QtCore, QtGui
import matplotlib.pyplot as plt

TEST_FILE = os.path.join(os.path.abspath(os.path.split(__file__)[0]), 'waxs', 'LSM_infl_228.hdf5')
HDF5_DATA_PATH = '/entry/data/data'
SCALING_FACTOR = 255        #  2**24


hdf5 = h5py.File(TEST_FILE)
ds = hdf5[HDF5_DATA_PATH]
image_data = numpy.ma.masked_less_equal(ds.value, 0)
image_data = image_data.filled(image_data.min())    # replace masked data with min good value
meta = dict(hi=image_data.max(), lo=image_data.min(), h=image_data.shape[0], w=image_data.shape[1])
log_image = numpy.log(image_data)
log_image -= log_image.min()
log_image *= SCALING_FACTOR / log_image.max()
int_log_image = numpy.array(log_image, dtype=int).tolist()

# http://pyside.github.io/docs/pyside/PySide/QtGui/QImage.html
# http://pyside.github.io/docs/pyside/PySide/QtGui/QImage.html#PySide.QtGui.PySide.QtGui.QImage.Format
qimage = QtGui.QImage(meta['w'], meta['h'], QtGui.QImage.Format_RGB32)
qimage.setPixel(2,3, QtGui.qRgb(10, 20, 30))

if False:
    # alternative:  PySide.QtGui.QImage.loadFromData(PySide.QtCore.QByteArray)
    #     # THIS IS SLOW
    ba = QtCore.QByteArray()
    ba.resize(meta['w'] * meta['h'])
    for r in range(meta['h']):
        for c in range(meta['w']):
            i = r*meta['w'] + c
            try:
                ba[i] = chr(int_log_image[r][c])
            except IndexError:
                print r, c, i
    qimage = QtGui.QImage.loadFromData(ba)  # wrong signature again!

# matplotlib
if False:
    plt.imshow(log_image)
    plt.colorbar()
    plt.show()

# print type(image_data), image_data.shape, image_data.max(), image_data.min()
# print log_image.shape, log_image.max(), log_image.min()
