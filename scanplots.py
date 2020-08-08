#!/usr/bin/env python

'''make plots of the last *n* scans in the scanlog'''


import datetime
import logging
import numpy
import os

import calc
import localConfig
import plot_mpl
import reduceAreaDetector
import reduceFlyData
import wwwServerTransfers
import xmlSupport


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
SCANLOG = '/share1/local_livedata/scanlog.xml'
NUMBER_SCANS_TO_PLOT = 5
scan_cache = None
spec_file_cache = None
scan_macro_list = "uascan sbuascan FlyScan sbFlyScan pinSAXS SAXS WAXS Flyscan".split()


class ScanCache(object):
    '''cache of scans already parsed'''
    # singleton class

    def __init__(self):
        self.db = {}

    def add(self, scan):
        key = scan.safe_id
        if key in self.db:
            raise KeyError(key + ' already in ScanCache')
        self.db[key] = scan

    def get(self, key):
        if key in self.db:
            return self.db[key]

    def get_keys(self):
        return self.db.keys()

    def delete(self, key):
        if key in self.db:
            del self.db[key]


class SpecFileObject(object):
    '''contents and metadata about a SPEC data file on disk'''

    def __init__(self, specfile):
        if os.path.exists(specfile):
            from spec2nexus.spec import SpecDataFile
            self.filename = specfile
            stat = os.stat(specfile)
            self.size = stat.st_size
            self.mtime = stat.st_mtime
            self.sdf_object = SpecDataFile(specfile)


class SpecFileCache(object):
    '''cache of SPEC data files already parsed'''
    # singleton class

    def __init__(self):
        self.db = {}    # index by file name

    def _add_(self, specfile):
        if specfile in self.db:
            raise KeyError(specfile + ' already in SpecFileCache')
        self.db[specfile] = SpecFileObject(specfile)
        return self.db[specfile]

    def get(self, specfile):
        if specfile in self.db:
            # check if file is unchanged
            cached = self.db[specfile]
            stat = os.stat(specfile)
            size = stat.st_size
            mtime = stat.st_mtime
            if mtime == cached.mtime and size == cached.size:
                return cached.sdf_object
            else:
                # reload if file has changed
                self._del_(specfile)

        return self._add_(specfile).sdf_object

    def get_keys(self):
        return self.db.keys()

    def _del_(self, key):
        if key in self.db:
            del self.db[key]


class Scan(object):
    '''details about a scan that could be plotted'''

    def __init__(self):
        self.title = None
        self.scan_type = None
        self.data_file = None
        self.scan_number = None
        self.scan_id = None
        self.spec_scan = None
        self.safe_id = None
        self.Q = None
        self.I = None

    def __str__(self, *args, **kwargs):
        return self.scan_type + ": " + self.title

    def setFileParms(self, title, data_file, scan_type, scan_number, scan_id):
        self.title = title
        self.scan_type = scan_type
        self.data_file = data_file
        self.scan_number = int(scan_number)
        self.scan_id = scan_id
        self.safe_id = self.makeSafeId()

    def makeSafeId(self):
        '''for use as HDF5 dataset name in HDF5 data file'''
        if self.spec_scan is None:
            self.getData()

        if self.spec_scan is None:
            logger.debug("No scan %d in file %s" % (self.scan_number, self.data_file))
            return None

        epoch = datetime.datetime.strptime(self.spec_scan.date, '%c')
        fmt = '%Y_%m_%d__%H_%M_%S'
        scan_date_time_stamp = datetime.datetime.strftime(epoch, fmt)

        self.safe_id = scan_date_time_stamp + '__%06d' % self.scan_number
        return self.safe_id

    def getSpecScan(self):
        global scan_cache
        global spec_file_cache
        if self.spec_scan is None:
            if self.safe_id is not None:
                # try to get scan from the scan cache
                self.spec_scan = scan_cache.get(self.safe_id)
            if self.spec_scan is None:
                # to get scan from the file cache
                spec = spec_file_cache.get(self.data_file)
                self.spec_scan = spec.getScan(str(self.scan_number))
        return self.spec_scan

    def getData(self):
        if self.scan_type in scan_macro_list:
            if self.spec_scan is None:
                self.spec_scan = self.getSpecScan()


def plottable_scan_node(scan_node):
    '''
    Determine if the scan_node (XML) is plottable

    :param obj scan_node: scan_node entry (instance of XML _Element node)
    :return obj: instance of Scan or None
    '''
    global scan_cache
    global spec_file_cache
    scan = None

    filename = scan_node.find('file').text.strip()
    if not os.path.exists(filename):
        return scan
    scan_type = scan_node.attrib['type']

    # TODO: #23 similar code blocks could be combined
    if scan_type in ('uascan', 'sbuascan'):
        if scan_node.attrib['state'] in ('scanning', 'complete'):
            if os.path.exists(filename):
                scan = Scan()
                scan.setFileParms(
                    scan_node.find('title').text.strip(),
                    filename,
                    scan_type,
                    scan_node.attrib['number'],
                    scan_node.attrib['id'],
                )
                scan.getData()

    elif scan_type in ('FlyScan', 'sbFlyScan', 'Flyscan'):
        if scan_node.attrib['state'] in ('complete', ):
            # specfiledir = os.path.dirname(filename)
            scan = Scan()
            scan.setFileParms(
                scan_node.find('title').text.strip(),
                filename,
                scan_type,
                scan_node.attrib['number'],
                scan_node.attrib['id'],
            )
            if scan.spec_scan is None:
                return None         # reached a dead end here
            scan.getData()

            # get the HDF5 file name from the SPEC file (no search needed)
            spec = spec_file_cache.get(filename)
            spec_scan = spec.getScan(str(scan_node.attrib['number']))
            if not spec_scan.__interpreted__:
                try:
                    spec_scan.interpret()
                except Exception as exc:
                    logger.error(str(exc))
                    return

            hdf5_file = get_Hdf5_Data_file_Name(spec_scan)
            if hdf5_file is None or not os.path.exists(hdf5_file):
                scan = None     # bail out, no HDF5 file found
            else:
                # actual data file
                scan_node.data_file = hdf5_file

    elif scan_type in ('pinSAXS', 'SAXS', 'WAXS',):
        if scan_node.attrib['state'] in ('complete', ):
            # specfiledir = os.path.dirname(filename)
            scan = Scan()
            scan.setFileParms(
                scan_node.find('title').text.strip(),
                filename,
                scan_type,
                scan_node.attrib['number'],
                scan_node.attrib['id'],
            )
            if scan.spec_scan is None:
                return None         # reached a dead end here
            scan.getData()
            if not scan.spec_scan.__interpreted__:
                try:
                    spec_scan.interpret()
                except Exception as exc:
                    logger.error(str(exc))
                    return

            hdf5_file = get_Hdf5_Data_file_Name(scan.spec_scan)
            if hdf5_file is not None and os.path.exists(hdf5_file):
                # actual data file
                scan_node.data_file = hdf5_file
            else:
                scan = None     # bail out, no HDF5 file found

    if scan is not None:
        scan_cache.add(scan)

    return scan


def last_n_scans(xml_log_file, number_scans):
    '''get list of last *n* plottable scan objects, chronological, most recent last'''
    xml_doc = xmlSupport.openScanLogFile(xml_log_file)
    if xml_doc is None:
        return []

    scans = []
    node_list = xml_doc.findall('scan') or []
    for scan_node in reversed(node_list):
        msg = scan_node.tag
        for k in "state type id".split():
            msg += " - " + scan_node.attrib[k]
        logger.debug(msg)
        scan_object = plottable_scan_node(scan_node)
        if scan_object is not None:
            scans.append(scan_object)
            if len(scans) == number_scans:
                break
    return list(reversed(scans))


def get_Hdf5_Data_file_Name(scan):
    """
    read the name of the HDF5 data file from the SPEC data file scan
    """
    scan_command_parts = scan.scanCmd.strip().split()
    if hasattr(scan, "MD"):
        # HDF5 data file (Flyscan, or area detector) written from Bluesky plan
        #MD hdf5_file = blank_0755.h5
        #MD hdf5_path = /share1/USAXS_data/2019-05/05_02_test_usaxs
        fname = scan.MD.get("hdf5_file")
        if fname is None:
            return "no spec data file"     # missing in an early version
        path = scan.MD["hdf5_path"]

    elif len(scan_command_parts) > 6 and scan_command_parts[0] in ("SAXS", "WAXS"):
        # EPICS area detector data file written from SPEC macros
        #S 10  WAXS  ./04_02_Cheng_INL_waxs/LaB6_0002.hdf     0    0    1    20     1
        #S 15  SAXS  ./04_02_Cheng_INL_saxs/BlankHeater_0003.hdf    0    0    1    20     1
        fname = scan_command_parts[1]
        path = os.path.dirname(scan.header.parent.fileName)

    elif len(scan_command_parts) > 3 and scan_command_parts[0] in ("FlyScan", ):
        # FlyScan HDF5 data file written from SPEC macros
        #C Tue Apr 02 20:49:39 2019.  FlyScan file name = ./04_02_Cheng_INL_usaxs/2104H_1020C_47min_0013.h5.
        comment = scan.comments[2]
        key_string = 'FlyScan file name = '
        index = comment.find(key_string) + len(key_string)
        fname = comment[index:-1]
        path = os.path.dirname(scan.header.parent.fileName)

    else:
        return

    hdf5_file = os.path.abspath(os.path.join(path, fname))
    return hdf5_file


def get_USAXS_FlyScan_Data(scan_obj):
    scan = scan_obj.spec_scan
    hdf5_file = get_Hdf5_Data_file_Name(scan)

    try:
        fly = reduceFlyData.UsaxsFlyScan(hdf5_file)  # checks if file exists
        #fly.make_archive()
        fly.reduce()        # open the file in this step
        fly.save(hdf5_file, 'full')
        if 'full' not in fly.reduced:
            return None
        fly.rebin(localConfig.REDUCED_FLY_SCAN_BINS)
        fly.save(hdf5_file, str(localConfig.REDUCED_FLY_SCAN_BINS))
    except IOError:
        return None     # file may not be available yet for reading if fly scan is still going
    except KeyError as exc:
        logger.info('HDF5 file:' + hdf5_file)
        raise KeyError(exc)
    except reduceFlyData.NoFlyScanData as _exc:
        logger.info(str(_exc))
        return None     # HDF5 file exists but length of raw data is zero

    fname = os.path.splitext(os.path.split(hdf5_file)[-1])[0]
    title = 'S%s %s (%s)' % (str(scan.scanNum), fname, 'fly')
    numbins_str = str(localConfig.REDUCED_FLY_SCAN_BINS)
    if numbins_str not in fly.reduced:
        return None
    rebinned = fly.reduced[numbins_str]
    entry = dict(qVec=rebinned['Q'], rVec=rebinned['R'], title=title)
    return entry


def get_AreaDetector_Data(scan_obj):
    scan = scan_obj.spec_scan
    scanMacro = scan.scanCmd.strip().split()[0].split("(")[0]
    hdf5_file = get_Hdf5_Data_file_Name(scan)
    bins = dict(SAXS=250, WAXS=800)[scanMacro]
    scan_name = os.path.splitext(os.path.split(hdf5_file)[-1])[0]

    ad = reduceAreaDetector.reduce_area_detector_data(hdf5_file,  bins)
    title = 'S%s %s (%s)' % (str(scan.scanNum), scan_name, scanMacro)
    rebinned = ad.reduced.get(str(bins))
    if rebinned is None:
        raise KeyError("No rebinned %s data of length %d" % (scanMacro, bins))
    rebinned = ad.reduced[str(bins)]
    entry = dict(qVec=rebinned['Q'], rVec=rebinned['R'], title=title)
    return entry


def get_USAXS_uascan_ScanData(scan, ar_center=None):
    usaxs = calc.reduce_uascan(scan.spec_scan)
    usaxs['qVec'] = usaxs.pop('Q')
    usaxs['rVec'] = usaxs.pop('R')
    usaxs['title'] = 'S' + str(scan.scan_number) + ' ' + scan.spec_scan.comments[0]
    return usaxs


def format_as_mpl_data_one(scan):
    '''prepare one USAXS scan for plotting with MatPlotLib'''
    try:
        Q = map(float, scan['qVec'])
        I = map(float, scan['rVec'])
    except TypeError as _e:
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


def get_USAXS_data(cache):
    mpl_datasets = []
    for key, scan_obj in sorted(cache.db.items()):
        # scan_obj = cache.get(key)
        if scan_obj is None:
            continue
        scanMacro = scan_obj.spec_scan.scanCmd.strip().split()[0].split("(")[0]
        if scanMacro in scan_macro_list:
            if scanMacro in ("uascan", "sbuascan"):
                try:
                    spec_scan.interpret()
                except Exception as exc:
                    logger.error(str(exc))
                    return
                entry = get_USAXS_uascan_ScanData(scan_obj)
            elif scanMacro in ("FlyScan", "sbFlyScan", "Flyscan"):
                entry = get_USAXS_FlyScan_Data(scan_obj)
            elif scanMacro in ("SAXS", "WAXS"):
                entry = get_AreaDetector_Data(scan_obj)
            mpl_ds = format_as_mpl_data_one(entry)
            if mpl_ds is None: continue
            if len(mpl_ds.Q) > 0 and len(mpl_ds.I) > 0:
                mpl_datasets.append(mpl_ds)
        logger.debug("{} = {}".format(key, scanMacro))
    return mpl_datasets


def save_temporary_test_data(mpl_datasets):
    '''save temporary test data sets'''
    from spec2nexus import eznx
    hdf5_file = os.path.join(localConfig.LOCAL_WWW_LIVEDATA_DIR, 'testdata.h5')
    f = eznx.makeFile(hdf5_file)
    for i, ds in enumerate(mpl_datasets):
        nxentry = eznx.makeGroup(f, 'entry_' + str(i), 'NXentry')
        eznx.makeDataset(nxentry, "title", ds.label)
        nxdata = eznx.makeGroup(nxentry, 'data', 'NXdata', signal='R', axes='Q')
        eznx.makeDataset(nxdata, "Q", ds.Q, units='1/A')
        eznx.makeDataset(nxdata, "R", ds.I, units='a.u.')
    f.close()


def main(n = None, cp=False):
    global scan_cache
    global spec_file_cache

    scan_cache = ScanCache()
    spec_file_cache = SpecFileCache()
    if n is None:
        n = NUMBER_SCANS_TO_PLOT
    scan_list = last_n_scans(SCANLOG, n)    # updates scan_cache & spec_file_cache
    logger.debug("scan list: " + ", ".join(map(str, scan_list)))

    local_plot = os.path.join(
        localConfig.LOCAL_WWW_LIVEDATA_DIR,
        localConfig.LOCAL_PLOTFILE)

    mpl_datasets = get_USAXS_data(scan_cache)
    if len(mpl_datasets):
        # save_temporary_test_data(mpl_datasets)
        try:
            plot_mpl.livedata_plot(mpl_datasets, local_plot)
        except plot_mpl.PlotException as exc:
            logger.info("{}".format(exc))
        if cp:
            www_plot = localConfig.LOCAL_PLOTFILE
            wwwServerTransfers.nfsCpToWebServer(local_plot, www_plot)


def pr20(n = None, cp=False):
    """
    test code

    make SAXS & WAXS data from BS show on livedata page

    supporting issue https://github.com/APS-USAXS/livedata/issues/14
    and PR https://github.com/APS-USAXS/livedata/pull/20

    import logging
    import os
    import scanplots

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    scanplots.pr20(100)
    """
    global scan_cache
    global spec_file_cache

    scan_cache = ScanCache()
    spec_file_cache = SpecFileCache()
    if n is None:
        n = NUMBER_SCANS_TO_PLOT
    last_n_scans(SCANLOG, n)    # updates scan_cache & spec_file_cache

    mpl_datasets = get_USAXS_data(scan_cache)

    logger.debug("scan list: ")
    for i, s in enumerate(mpl_datasets):
        logger.debug("%d  %d  %s" % (i+1, len(s.Q), s.label))


if __name__ == "__main__":
    #last_n_scans(SCANLOG, NUMBER_SCANS_TO_PLOT)
    main()
