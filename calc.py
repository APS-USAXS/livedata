#!/usr/bin/env python

"""
Calculate R(Q) from arrays of measured data using numpy
"""


import datetime
import h5py
import logging
import math
import numpy
import pathlib
import spec2nexus.eznx
import spec2nexus.spec


logger = logging.getLogger(__name__)

USAXS_DATA = pathlib.Path("/share1/USAXS_data")
TESTDATA = pathlib.Path(__file__).parent / "data"

# TEST_FILE_FLYSCAN = TESTDATA / 'S217_E7_600C_87min.h5'
TEST_FILE_FLYSCAN = TESTDATA / "Blank_0016.h5"
# TEST_FILE_FLYSCAN = TESTDATA / "S6_r1SOTy2_0235.h5"
# TEST_FILE_UASCAN = TESTDATA / '03_18_GlassyCarbon.dat'
# TEST_UASCAN_SCAN_NUMBER = 522
# TEST_FILE_UASCAN = USAXS_DATA / "2021-09/09_18_test/09_18_test.dat"
# TEST_UASCAN_SCAN_NUMBER = 11
TEST_FILE_UASCAN = USAXS_DATA / "2022-11/11_03_24keVTest/11_03_24keVTest.dat"
TEST_UASCAN_SCAN_NUMBER = 248
TEST_FILE_OUTPUT = TESTDATA / "test_calc.h5"

CUTOFF = 0.4  # when calculating the center, look at data above CUTOFF*R_max
ZINGER_THRESHOLD = 2


class FileNotFound(RuntimeError):
    pass


def calc_R_Q(
    wavelength,
    ar,
    seconds,
    pd,
    pd_bkg,
    pd_gain,
    I0,
    I0_bkg=None,
    I0_gain=None,
    ar_center=None,
    V_f_gain=None,
):
    """
    Calculate :math:`R(Q)`

    :param float wavelength: :math:`lambda`, (:math:`\A`)
    :param float ar_center: center of rocking curve along AR axis
    :param numpy.ndarray([float]) ar: array of crystal analyzer angles
    :param numpy.ndarray([float]) seconds: array of counting time for each point
    :param numpy.ndarray([float]) pd: array of photodiode counts
    :param numpy.ndarray([float]) pd_bkg: array of photodiode amplifier backgrounds
    :param numpy.ndarray([float]) pd_gain: array of photodiode amplifier gains
    :param numpy.ndarray([float]) I0: array of incident monitor counts
    :param numpy.ndarray([float]) I0_bkg: array of I0 backgrounds
    :param numpy.ndarray([float]) I0_amp_gain: array of I0 amplifier gains
    :param numpy.ndarray([float]) V_f_gain: array of voltage-frequency converter gains
    :returns dictionary: Q, R
    :param numpy.ndarray([float]) qVec: :math:`Q`
    :param numpy.ndarray([float]) rVec: :math:`R = I/I_o`
    """
    r = amplifier_corrections(pd, seconds, pd_bkg, pd_gain)
    r0 = amplifier_corrections(I0, seconds, I0_bkg, I0_gain)

    rVec = r / r0
    if V_f_gain is not None:  # but why?
        rVec /= V_f_gain
    rVec = numpy.ma.masked_less_equal(rVec, 0)

    ar_r_peak = ar[numpy.argmax(rVec)]  # ar value at peak R
    rMax = rVec.max()
    if ar_center is None:  # compute ar_center from rVec and ar
        ar_center = centroid(ar, rVec)  # centroid of central peak

    d2r = math.pi / 180
    qVec = (4 * math.pi / wavelength) * numpy.sin(d2r * (ar_center - ar) / 2)

    # trim off masked points
    r0 = remove_masked_data(r0, rVec.mask)
    r = remove_masked_data(r, rVec.mask)
    ar = remove_masked_data(ar, rVec.mask)
    qVec = remove_masked_data(qVec, rVec.mask)
    rVec = remove_masked_data(rVec, rVec.mask)

    result = dict(
        Q=qVec,
        R=rVec,
        ar=ar,
        r=r,
        r0=r0,
        ar_0=ar_center,
        ar_r_peak=ar_r_peak,
        r_peak=rMax,
    )
    return result


def amplifier_corrections(signal, seconds, dark, gain):
    """
    correct for amplifier dark current and gain

    :math:`v = (s - t*d) / g`
    """
    # v = (signal - seconds*dark) / gain
    v = numpy.array(signal, dtype=float)
    if dark is not None:  # compatibility with older USAXS data
        v = numpy.ma.masked_less_equal(v - seconds * dark, 0)
    if gain is not None:  # compatibility with older USAXS data
        gain = numpy.ma.masked_less_equal(gain, 0)
        v /= gain
    return v


def centroid(x, y):
    """compute centroid of y(x)"""
    import scipy.integrate

    def zinger_test(u, v):
        m = max(v)
        p = numpy.where(v == m)[0][0]
        top = (v[p - 1] + v[p] + v[p + 1]) / 3
        bot = (v[p - 1] + v[p + 1]) / 2
        v_test = top / bot
        logger.debug("zinger test: %f", v_test)
        return v_test

    a = remove_masked_data(x, y.mask)
    b = remove_masked_data(y, y.mask)

    while zinger_test(a, b) > ZINGER_THRESHOLD:
        R_max = max(b)
        peak_index = numpy.where(b == R_max)[0][0]
        # delete or mask x[peak_index], and y[peak_index]
        logger.debug("removing zinger at ar = %f", a[peak_index])
        a = numpy.delete(a, peak_index)
        b = numpy.delete(b, peak_index)

    # gather the data nearest the peak (above the CUTOFF)
    R_max = max(b)
    cutoff = R_max * CUTOFF
    peak_index = numpy.where(b == R_max)[0][0]
    n = len(a)

    # walk down each side from the peak
    pLo = peak_index
    while pLo >= 0 and b[pLo] > cutoff:
        pLo -= 1

    pHi = peak_index + 1
    while pHi < n and b[pHi] > cutoff:
        pHi += 1

    # enforce boundaries
    pLo = max(0, pLo + 1)  # the lowest ar above the cutoff
    pHi = min(n - 1, pHi)  # the highest ar (+1) above the cutoff

    if pHi - pLo == 0:
        emsg = "not enough data to find peak center - not expected"
        logger.debug(emsg)
        raise KeyError(emsg)
    elif pHi - pLo == 1:
        # trivial answer
        emsg = "peak is 1 point, picking peak position as center"
        logger.debug(emsg)
        return x[peak_index]

    a = a[pLo:pHi]
    b = b[pLo:pHi]

    weight = b * b
    top = scipy.integrate.simps(a * weight, a)
    bottom = scipy.integrate.simps(weight, a)
    center = top / bottom

    emsg = "computed peak center: " + str(center)
    logger.debug(emsg)
    return center


def remove_masked_data(data, mask):
    """remove all masked data, convenience routine"""
    arr = numpy.ma.masked_array(data=data, mask=mask)
    return arr.compressed()


def test_flyScan(filename):
    """test data reduction from a flyScan (in an HDF5 file)"""
    if not filename.exists():
        raise FileNotFound(filename)

    import reduceFlyData

    fs = reduceFlyData.UsaxsFlyScan(filename)
    # compute the R(Q) profile
    fs.reduce()
    usaxs = fs.reduced
    return usaxs


def test_uascan(filename):
    """test data reduction from an uascan (in a SPEC file)"""
    if not filename.exists():
        raise FileNotFound(filename)

    # open the SPEC data file
    sdf_object = spec2nexus.spec.SpecDataFile(filename)
    sds = sdf_object.getScan(TEST_UASCAN_SCAN_NUMBER)
    sds.interpret()
    return reduce_uascan(sds)


def reduce_uascan(sds):
    """data reduction of an uascan (in a SPEC file)

    :params obj sds: spec2nexus.spec.SpecDataFileScan object
    :returns: dictionary of title and R(Q)
    """
    # get the raw data from the data file
    created_by_bluesky = sds.header.comments[0].startswith("Bluesky ")
    if not created_by_bluesky:  # SPEC created this data file
        wavelength = float(sds.metadata["DCM_lambda"])
        ar = numpy.array(sds.data["ar"])
        seconds = numpy.array(sds.data["seconds"])
        pd = numpy.array(sds.data["pd_counts"])
        I0 = numpy.array(sds.data["I0"])
        I0_amplifier_gain = numpy.array(sds.metadata["I0AmpGain"])
        pd_range = numpy.array(sds.data["pd_range"], dtype=int)
        ar_center = float(sds.metadata["arCenter"])

        # gain & dark are stored as 1-offset, pad here with 0-offset to simplify list handling
        gain = [
            0,
        ] + map(lambda _: sds.metadata["UPD2gain" + str(_)], range(1, 6))
        dark = [
            0,
        ] + map(lambda _: sds.metadata["UPD2bkg" + str(_)], range(1, 6))

        # create numpy arrays to match the ar & pd data
        pd_gain = map(lambda _: gain[_], pd_range)
        pd_dark = map(lambda _: dark[_], pd_range)
    else:  # Bluesky created this data file
        # BS plan writes a NeXus file with the raw data.
        # rebuild the full HDF5 data file name
        filename = pathlib.Path(sds.MD["hdf5_path"]) / sds.MD["hdf5_file"]
        if not filename.exists():
            raise FileNotFoundError("Could not find uascan data file: %s", filename)

        with h5py.File(filename, "r") as root:
            # get all data from the HDF5 file
            entry = root["/entry"]
            baseline = entry["instrument/bluesky/streams/baseline"]
            primary = entry["instrument/bluesky/streams/primary"]

            # Must copy from h5py into local data to keep once h5py file is closed.
            wavelength = entry["instrument/monochromator/wavelength"][()]
            ar = primary["a_stage_r/value"][()]
            pps = sds.MD.get("scaler_pulses_per_second", 1e-7)
            seconds = pps * primary["seconds/value"][()]  # convert from counts
            pd = primary["PD_USAXS/value"][()]
            I0 = primary["I0_USAXS/value"][()]
            I0_amplifier_gain = primary["I0_autorange_controls_gain/value"][()]
            ar_center = baseline["terms_USAXS_center_AR/value_start"][()]

            pd_gain = primary["upd_autorange_controls_gain/value"][()]

            pd_range = primary["upd_autorange_controls_reqrange/value"]
            bkg = []
            for ch in range(5):
                addr = "upd_autorange_controls_ranges_gain%d_background" % ch
                bkg.append(baseline[addr + "/value_start"][()])
            pd_dark = [bkg[i] for i in pd_range]

    # compute the R(Q) profile
    usaxs = calc_R_Q(
        wavelength,
        ar,
        seconds,
        pd,
        pd_dark,
        pd_gain,
        I0,
        I0_gain=I0_amplifier_gain,
        ar_center=ar_center,
    )
    return usaxs


def iso8601_datetime():
    """
    Return current date & time as modified ISO8601=compliant string.

    Standard ISO8601 uses 'T', blank space instead is now allowed.
    """
    return datetime.datetime.now().isoformat(sep=" ")


def bin_xref(x, bins):
    """
    Return an array of arrays.
    Outer array is in bins, inner array contains indices of x in each bin,

    :param ndarray x: values to be mapped
    :param ndarray bins: new bin boundaries
    """
    indices = numpy.digitize(x, bins)
    xref_dict = {}
    for i, v in enumerate(indices):
        if 0 < v < len(bins):
            if str(v) not in xref_dict:
                xref_dict[str(v)] = []
            xref_dict[str(v)].append(i)
    key_list = map(int, xref_dict.keys())
    xref = [xref_dict[str(key)] for key in sorted(key_list)]
    return numpy.array(xref)


def developer_main():
    hdf5FileName = TEST_FILE_FLYSCAN
    # fs = test_flyScan(hdf5FileName)

    specFileName = TEST_FILE_UASCAN
    ua = test_uascan(TEST_FILE_UASCAN)

    # - - - - - - - - - - - - - - - - - - - - - - - - - -

    # write results to a NeXus file

    nx = spec2nexus.eznx.makeFile(
        str(TEST_FILE_OUTPUT),
        signal="flyScan",
        timestamp=str(datetime.datetime.now()),
        writer="USAXS livedata.calc and spec2nexus.eznx",
        purpose="testing common USAXS calculation code on different scan file types",
    )

    nxentry = spec2nexus.eznx.makeGroup(nx, "flyScan", "NXentry", signal="data")
    nxentry.create_dataset("title", data=str(hdf5FileName))
    nxdata = spec2nexus.eznx.makeGroup(nxentry, "data", "NXdata", signal="R", axes="Q")
    # for k, v in sorted(fs["full"].items()):
    #     spec2nexus.eznx.makeDataset(nxdata, k, v)

    nxentry = spec2nexus.eznx.makeGroup(nx, "uascan", "NXentry", signal="data")
    nxentry.create_dataset("title", data=str(specFileName))
    nxdata = spec2nexus.eznx.makeGroup(nxentry, "data", "NXdata", signal="R", axes="Q")
    for k, v in sorted(ua.items()):
        spec2nexus.eznx.makeDataset(nxdata, k, v)

    nx.close()


if __name__ == "__main__":
    developer_main()
