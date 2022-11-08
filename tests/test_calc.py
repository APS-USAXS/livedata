import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from calc import reduce_uascan
from spec2nexus.spec import SpecDataFile
import h5py
import pytest


USAXS_DATA = pathlib.Path("/share1/USAXS_data")
TESTDATA = pathlib.Path(__file__).parent.parent / "data"

TEST_FILE_OUTPUT = TESTDATA / "test_calc.h5"


@pytest.mark.parametrize(
    "filename",
    [
        TESTDATA / "S217_E7_600C_87min.h5",
        TESTDATA / "Blank_0016.h5",
        TESTDATA / "S6_r1SOTy2_0235.h5",
    ]
)
def test_flyScan(filename):
    """test data reduction from a flyScan (in an HDF5 file)"""
    if not filename.exists():
        raise FileNotFoundError(filename)
    assert filename.exists()

    import reduceFlyData

    fs = reduceFlyData.UsaxsFlyScan(filename)
    with h5py.File(filename, "r") as root:
        amp_name = fs.get_USAXS_PD_amplifier_name(root)
        assert amp_name == "DDPCA300"
        assert isinstance(amp_name, str)
        changes = fs.get_range_changes(root, amp_name)
        arr_channel, arr_requested, arr_actual = changes
        assert len(arr_channel) == len(arr_requested)
        assert len(arr_channel) == len(arr_actual)
    # compute the R(Q) profile
    fs.reduce()
    usaxs = fs.reduced
    assert usaxs is not None
    assert isinstance(usaxs, dict)
    assert "full" in usaxs


@pytest.mark.parametrize(
    "filename, scan_number",
    [
        [TESTDATA / '03_18_GlassyCarbon.dat', 522],
        [USAXS_DATA / "2021-09/09_18_test/09_18_test.dat", 11],
        [USAXS_DATA / "2022-11/11_03_24keVTest/11_03_24keVTest.dat", 248],
    ]
)
def test_uascan(filename, scan_number):
    """test data reduction from an uascan (in a SPEC file)"""
    if not filename.exists():
        raise FileNotFoundError(filename)

    # open the SPEC data file
    sdf_object = SpecDataFile(filename)
    assert isinstance(sdf_object, SpecDataFile)

    sds = sdf_object.getScan(scan_number)
    assert sds is not None
    # TODO: anything to test _before_ interpret?

    sds.interpret()
    # TODO: anything to test now?

    uascan = reduce_uascan(sds)
    assert isinstance(uascan, dict)  # data is reduceable
    for k in "Q R ar r r0  ar_0  ar_r_peak  r_peak".split():
        assert k in uascan

    # same lengths
    n = len(uascan["Q"])
    for k in "R ar".split():
        assert len(uascan[k]) == n


# TODO: refactor as test(s)
# def developer_main():
#     hdf5FileName = TEST_FILE_FLYSCAN
#     # fs = test_flyScan(hdf5FileName)

#     specFileName = TEST_FILE_UASCAN
#     ua = test_uascan(TEST_FILE_UASCAN)

#     # - - - - - - - - - - - - - - - - - - - - - - - - - -

#     # write results to a NeXus file

#     nx = spec2nexus.eznx.makeFile(
#         str(TEST_FILE_OUTPUT),
#         signal="flyScan",
#         timestamp=str(datetime.datetime.now()),
#         writer="USAXS livedata.calc and spec2nexus.eznx",
#         purpose="testing common USAXS calculation code on different scan file types",
#     )

#     nxentry = spec2nexus.eznx.makeGroup(nx, "flyScan", "NXentry", signal="data")
#     nxentry.create_dataset("title", data=str(hdf5FileName))
#     nxdata = spec2nexus.eznx.makeGroup(nxentry, "data", "NXdata", signal="R", axes="Q")
#     # for k, v in sorted(fs["full"].items()):
#     #     spec2nexus.eznx.makeDataset(nxdata, k, v)

#     nxentry = spec2nexus.eznx.makeGroup(nx, "uascan", "NXentry", signal="data")
#     nxentry.create_dataset("title", data=str(specFileName))
#     nxdata = spec2nexus.eznx.makeGroup(nxentry, "data", "NXdata", signal="R", axes="Q")
#     for k, v in sorted(ua.items()):
#         spec2nexus.eznx.makeDataset(nxdata, k, v)

#     nx.close()
