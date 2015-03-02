#!/usr/bin/env python

'''make plots of the last *n* scans in the scanlog'''


import datetime
import glob
import os
import spec2nexus.spec

import localConfig
import plot
import plot_mpl
import reduceFlyData
import wwwServerTransfers
import xmlSupport


SCANLOG = '/share1/local_livedata/scanlog.xml'
NUMBER_SCANS_TO_PLOT = 5
scan_cache = None
spec_file_cache = None


###########
###########  THIS MODULE IS BEING DEVELOPED
###########  IT IS NOT READY FOR PRODUCTION USE
###########


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
            self.filename = specfile
            stat = os.stat(specfile)
            self.size = stat.st_size
            self.mtime = stat.st_mtime
            self.sdf_object = spec2nexus.spec.SpecDataFile(specfile)


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
                self.spec_scan = spec.getScan(self.scan_number)
        return self.spec_scan

    def getData(self):
        if self.scan_type in ('uascan', 'sbuascan'):
            if self.spec_scan is None:
                self.spec_scan = self.getSpecScan()
            # TODO: reduce the USAXS raw data
        elif self.scan_type in ('FlyScan'):
            if self.spec_scan is None:
                self.spec_scan = self.getSpecScan()
            # TODO: reduce
            pass
        elif self.scan_type in ('pinSAXS'):
            pass
        elif self.scan_type in ('WAXS'):
            pass
        else:
            pass


def plottable_scan(scan_node):
    '''
    Determine if the scan_node (XML) is plottable
    
    :param obj scan_node: scan_node entry (instance of XML _Element node)
    :return obj: instance of Scan or None
    '''
    global scan_cache
    global spec_file_cache
    scan = None
    
    filename = scan_node.find('file').text.strip()
    if scan_node.attrib['type'] in ('uascan', 'sbuascan'):
        if scan_node.attrib['state'] in ('scanning', 'complete'):
            if os.path.exists(filename):
                scan = Scan()
                scan.setFileParms(
                    scan_node.find('title').text.strip(),
                    filename,
                    scan_node.attrib['type'],
                    scan_node.attrib['number'],
                    scan_node.attrib['id'],
                )
                scan.getData()

    elif scan_node.attrib['type'] in ('FlyScan', ):
        if scan_node.attrib['state'] in ('complete', ):
            specfiledir = os.path.dirname(filename)
            scan = Scan()
            scan.setFileParms(
                scan_node.find('title').text.strip(),
                filename,
                scan_node.attrib['type'],
                scan_node.attrib['number'],
                scan_node.attrib['id'],
            )
            scan.getData()

            # get the HDF5 file name from the SPEC file (no search needed)
            spec = spec_file_cache.get(filename)
            spec_scan = spec.getScan(int(scan_node.attrib['number']))
            for line in spec_scan.comments:
                if line.find('FlyScan file name = ') > 1:
                    hdf5_file = line.split('=')[-1].strip().rstrip('.')
                    hdf5_file = os.path.abspath(os.path.join(specfiledir, hdf5_file))
                    if os.path.exists(hdf5_file):
                        # actual data file
                        scan_node.data_file = hdf5_file
                        ok = True
                    else:
                        scan = None     # bail out, no HDF5 file found
                    break

    if scan is not None:
        scan_cache.add(scan)

    return scan


def last_n_scans(xml_log_file, number_scans):
    '''get list of last *n* plottable scan objects, chronological, most recent last'''
    xml_doc = xmlSupport.openScanLogFile(xml_log_file)

    scans = []
    node_list = xml_doc.findall('scan')
    if node_list is not None:
        for scan_node in reversed(node_list):
            scan_object = plottable_scan(scan_node)
            if scan_object is not None:
                scans.append(scan_object)
                if len(scans) == number_scans:
                    break
    return list(reversed(scans))


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


def get_USAXS_Uascan_ScanData(scan):
    return plot.calc_usaxs_data(scan.spec_scan)


def get_USAXS_FlyScan_Data(scan_obj):
    scan = scan_obj.spec_scan
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
    return entry


def get_USAXS_data(cache):
    import plot
    getscandata = dict(uascan=get_USAXS_Uascan_ScanData, 
                       sbuascan=get_USAXS_Uascan_ScanData, 
                       FlyScan=get_USAXS_FlyScan_Data)
    mpl_datasets = []
    for key in sorted(cache.get_keys()):
        scan_obj = cache.get(key)
        scanMacro = scan_obj.spec_scan.scanCmd.strip().split()[0]
        if scanMacro in getscandata.keys():
            if scan_obj is None: continue
            entry = getscandata[scanMacro](scan_obj)
            mpl_ds = plot.format_as_mpl_data_one(entry)
            if mpl_ds is None: continue
            if len(mpl_ds.Q) > 0 and len(mpl_ds.I) > 0:
                mpl_datasets.append(mpl_ds)
        # print key, scanMacro
    return mpl_datasets

def main(n = None, cp=False):
    global scan_cache
    global spec_file_cache

    scan_cache = ScanCache()
    spec_file_cache = SpecFileCache()
    if n is None:
        n = NUMBER_SCANS_TO_PLOT
    scans = last_n_scans(SCANLOG, n)

    local_plot = os.path.join(
                              localConfig.LOCAL_WWW_LIVEDATA_DIR, 
                              localConfig.LOCAL_PLOTFILE)

    mpl_datasets = get_USAXS_data(scan_cache)
    if len(mpl_datasets):
        if False:
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
        plot_mpl.livedata_plot(mpl_datasets, local_plot)
        if cp:
            www_plot = localConfig.LOCAL_PLOTFILE
            wwwServerTransfers.scpToWebServer(local_plot, www_plot)


#**************************************************************************

if __name__ == "__main__":
    main()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $HeadURL$
# $Id$
########### SVN repository information ###################
