#!/usr/bin/env python

'''
read a SPEC data file and plot the last n USAXS scans for the livedata WWW page

.. note:: copies plot file to USAXS site on XSD WWW server
'''

import math
import numpy
import os

from spec2nexus import prjPySpec        # read SPEC data files
# TODO: refactor with spec2nexus.spec

import localConfig      # definitions for 9-ID
import wwwServerTransfers
import reduceFlyData
import plot_mpl


scanlog_mtime = None
usaxs_scans_cache = []
spec_file_cache = {}
PLOT_SUPPORT = 'MatPlotLib'


class Scan(object):
    '''representation of a USAXS scan'''
    
    file = None
    number = -1
    title = ''
    started = ''
    specscan = None
    qVec = []
    rVec = []


def update_n_plots(specFile, numScans):
    '''read the SPEC file and grab n scans'''
    sd = prjPySpec.SpecDataFile(specFile)
    scanList = last_n_scans(sd.scans, numScans)
    if len(scanList) == 0:
        return

    usaxs = extract_USAXS_data(sd, scanList)  # extract R(Q), ignoring errors
    if usaxs is None:
        return

    local_plot = os.path.join(
                              localConfig.LOCAL_WWW_LIVEDATA_DIR, 
                              localConfig.LOCAL_PLOTFILE)

    # use MatPlotLib to plot the USAXS livedata (BCDA_09ID-57)
    mpl_data = format_as_mpl_data(usaxs)
    if len(mpl_data) == 0:
        return usaxs
    plot_mpl.livedata_plot(mpl_data, local_plot, specFile)

    www_plot = localConfig.LOCAL_PLOTFILE
    wwwServerTransfers.scpToWebServer(local_plot, www_plot)
    # perhaps copy the SPEC macro here, as well
    
    return usaxs


def last_n_scans(scans, maxScans):
    '''
    find the last maxScans scans in the specData
    
    :param scans: SpecDataFileScan instance list
    :param int maxScans: maximum number of scans to find
    :return: list of SpecDataFileScan objects where len() <= maxScans
    '''
    scanList = []
    for scan in scans.values():
        cmd = scan.scanCmd.split()[0]
        if cmd in ('uascan', 'sbuascan', 'FlyScan'):
            scanList.append(scan)
            if len(scanList) > maxScans:
                scanList.pop(0)
    return scanList


def extract_USAXS_data(specData, scanList):
    '''
    extract the USAXS R(Q) profiles (ignoring error estimates)

    :param specData: as returned by prjPySpec.SpecDataFile(specFile)
    :param scanList: list of SpecDataFileScan objects
    :return: list of dictionaries with reduced USAXS R(Q)
    '''
    usaxs = []
    for scan in scanList:
        if scan.scanCmd.strip().split()[0] in ('FlyScan',):
            #hdf5File = scan.comments[2].split()[-1][:-2]

            comment = scan.comments[2]
            key_string = 'FlyScan file name = '
            index = comment.find(key_string) + len(key_string)
            fname = comment[index:-1]
            path = os.path.dirname(scan.header.parent.fileName)
            hdf5File = os.path.abspath(os.path.join(path, fname))

            try:
                fly = reduceFlyData.UsaxsFlyScan(hdf5File)  # checks if file exists
                #fly.make_archive()
                fly.reduce()        # open the file in this step
                fly.save(hdf5File, 'full')
                fly.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
                fly.save(hdf5File, str(localConfig.REDUCED_FLY_SCAN_BINS))
            except IOError:
                return None     # file may not be available yet for reading if fly scan is still going
            title = os.path.split(hdf5File)[-1] + '(fly)'
            rebinned = fly.reduced[str(localConfig.REDUCED_FLY_SCAN_BINS)]
            entry = dict(qVec=rebinned['Q'], rVec=rebinned['R'], title=title)
        else:
            entry = calc_usaxs_data(scan)
        entry['scan'] = scan.scanNum
        entry['key'] = "S%d" % scan.scanNum
        entry['label'] = "%s: %s" % (entry['key'], entry['title'])
        usaxs.append( entry )
    return usaxs


def format_as_mpl_data(usaxs):
    '''prepare the USAXS data for plotting with MatPlotLib'''
    mpl_datasets = []
    for scan in usaxs:
        if scan is not None:
            mpl_ds = format_as_mpl_data_one(scan)
            if mpl_ds is None: continue
            if len(mpl_ds.Q) > 0 and len(mpl_ds.I) > 0:
                mpl_datasets.append(mpl_ds)
    return mpl_datasets


def format_as_mpl_data_one(scan):
    '''prepare one USAXS scan for plotting with MatPlotLib'''
    try:
        Q = map(float, scan['qVec'])
        I = map(float, scan['rVec'])
    except TypeError, _e:
        if scan is None: return None
        Q = scan['qVec']
        I = scan['rVec']
    Q = numpy.ma.masked_less_equal(numpy.abs(Q), 0)
    I = numpy.ma.masked_less_equal(I, 0)
    mask = numpy.ma.mask_or(Q.mask, I.mask)
    
    mpl_ds = plot_mpl.Plottable_USAXS_Dataset()
    mpl_ds.Q = numpy.ma.masked_array(data=Q, mask=mask).compressed()
    mpl_ds.I = numpy.ma.masked_array(data=I, mask=mask).compressed()
    mpl_ds.label = scan['title']

    if len(mpl_ds.Q) > 0 and len(mpl_ds.I) > 0:
        return mpl_ds


def calc_usaxs_data(specScan):
    '''
    calculate USAXS R(Q) from raw SPEC scan data, return as a dict
    
    :params obj specScan: prjPySpec.SpecDataFileScan object
    :returns: dictionary of title and R(Q)
    '''
    # TODO: refactor with numpy
    d2r = math.pi / 180
    sampleTitle = specScan.comments[0]
    arCenter = specScan.positioner['ar']
    wavelength = specScan.metadata['DCM_lambda']
    if wavelength == 0:      # TODO: development ONLY
        wavelength = localConfig.A_keV/specScan.metadata['DCM_energy']
    numData = len(specScan.data['pd_counts'])
    USAXS_Q = []
    USAXS_I = []
    V_f_gain = localConfig.FIXED_VF_GAIN
    for i in range(numData):
        pd_counts = specScan.data['pd_counts'][i]
        pd_range = specScan.data['pd_range'][i]
        ar_enc = specScan.data['ar_enc'][i]
        seconds = specScan.data['seconds'][i]
        I0_gain = specScan.data['I0_gain'][i]
        if I0_gain <= 0:  I0_gain = 1			# safeguard
        I0 = 1.0*specScan.data['I0'][i] / I0_gain
        if I0 == 0:  I0 = 1      # TODO: development ONLY
        index = str(int(pd_range))
        diode_gain = specScan.metadata["UPD2gain" + index]
        dark_curr = specScan.metadata["UPD2bkg" + index]
        #----
        qVec = (4 * math.pi / wavelength) * math.sin(d2r*(arCenter - ar_enc)/2)
        rVec = (pd_counts - seconds*dark_curr) / diode_gain / I0 / V_f_gain
        #----
        USAXS_Q.append( str(qVec) )
        USAXS_I.append( str(rVec) )
    return dict(title=sampleTitle, qVec=USAXS_Q, rVec=USAXS_I)


def identify_last_n_scans(numScans):
    '''refresh the cache of the last N scans, return list in case it is wanted'''
    global scanlog_mtime, usaxs_scans_cache
    # optimize this to avoid reptitive file scanning and sorting
    # cache the results
    scanlog_file = os.path.abspath('/share1/local_livedata/scanlog.xml')
    if not os.path.exists(scanlog_file):
        raise IOError, 'scanlog file not found: ' + scanlog_file
    mtime = os.path.getmtime(scanlog_file)      # compare against the cache to optimize
    if mtime == scanlog_mtime and numScans == len(usaxs_scans_cache):
        return usaxs_scans_cache
    scanlog_mtime = mtime
    
    from lxml import etree as lxml_etree        # in THIS routine, use lxml's etree, it has xpath
    scanlog = lxml_etree.parse(scanlog_file)
    # assumption: the scans are logged in chronological order
    # otherwise, need to compare the "started" element for attributes @date and @time
    xpath_str = '/USAXS_SCAN_LOG/scan[position() >= last()-%d]' % (numScans - 1)
    scans = scanlog.xpath(xpath_str)
    db = []
    for scan in scans:
        started = scan.find('started')
        record = Scan()
        record.file = scan.find('file').text
        record.number = int(scan.get('number', '-1'))
        record.title = scan.find('title').text
        record.started = started.get('date', '') + ' ' + started.get('time', '')
        db.append(record)
    usaxs_scans_cache = db
    # ready to read scan data now
    return db


def get_spec_data():
    '''read SPEC data files, get USAXS data from the chosen scans'''
    global spec_file_cache, usaxs_scans_cache
    
    # TODO: cache reduced R(Q) data in an HDF5 file
    # this allows to view scans from different data files together
    # also allows to show reduced fly scan data as well as reduced image data
    
    # optimize using a cache for the SPEC data files in recent use
    # add any new spec files
    files_in_use = []
    for usaxs_scan in usaxs_scans_cache:
        if usaxs_scan.file not in spec_file_cache:
            if not os.path.exists(usaxs_scan.file):
                raise IOError, 'spec data file not found: ' + usaxs_scan.file
            # TODO: refactor
            spec_file_cache[usaxs_scan.file] = prjPySpec.SpecDataFile(usaxs_scan.file)
        if usaxs_scan.file not in files_in_use:
            files_in_use.append(usaxs_scan.file)
    # discard unused spec files from RAM
    for specfile in spec_file_cache.keys():
        if specfile not in files_in_use:
            del spec_file_cache[specfile]
    del files_in_use
    
    # find the spec data for each scan
    for usaxs_scan in usaxs_scans_cache:
        sfd = spec_file_cache[usaxs_scan.file]
        # search by exhaustion for the scan data
        found = False
        for specscan in sfd.scans.values():
            if specscan.scanNum == usaxs_scan.number:
                found = True
                break
        if not found:
            continue    # TODO: is this the right thing to do?

        # get R(Q) from the SPEC scan
        entry = calc_usaxs_data(specscan)
        # store it in the Scan object
        usaxs_scan.specscan = specscan
        usaxs_scan.qVec = entry['qVec']
        usaxs_scan.rVec = entry['rVec']
        # ready for plotting now


def developer_main():
    numScans = 5
    usaxs_scans_cache = identify_last_n_scans(numScans)
    # note: cache is the same as usaxs_scans_cache
    # TODO:


if __name__ == '__main__':
    developer_main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
