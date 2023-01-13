
'''developer routine to test reduceAreaDetector.py'''

import os
import sys

import plot_mpl
import reduceAreaDetector
import pvwatch

# sys.argv = [sys.argv[0],]
#sys.argv.append( '-h' )
#sys.argv.append( '-V' )
#sys.argv.append( '-n 250' )
sys.argv.append( '--recompute-full' )
sys.argv.append( '--recompute-rebinned' )

#path = os.environ.get('HOMEPATH', None)
path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(path, 'testdata')

testfiles = []
path = os.path.join(path, '2016-02-27')
testfiles.append(os.path.join(path, '02_27_AlCe_saxs', 'A_AlCe_3433.hdf'))
testfiles.append(os.path.join(path, '02_27_AlCe_waxs', 'A_AlCe_2849.hdf'))

testfiles = []
# testfiles.append("/share1/USAXS_data/2021-12/12_10_DexHeater/12_10_DexHeater_waxs/Ti64Dex_975C_99min_000399.hdf")
testfiles.append(
    "/share1/USAXS_data/2021-12/"
    "12_20_TestDex/12_20_TestDex_waxs/"
    "DexTest_000555.hdf"
)

argv = list(sys.argv)

for hdf5_file in testfiles:
    sys.argv = list(argv)
    sys.argv.append( hdf5_file )
    path = os.path.dirname(hdf5_file)
    scan = reduceAreaDetector.command_line_interface()

    plotfile = os.path.join(path, 'test_specplot__' + os.path.basename(hdf5_file) + '_.png')

    plot_mpl.spec_plot(
        scan.reduced['full']['Q'], scan.reduced['full']['R'],
        plotfile,
        xtitle='Q', ytitle='R',
        ylog=True,
        )

    plotfile = os.path.join(path, 'test_usaxsplot_' + os.path.basename(hdf5_file) + '_.png')
    ds_full = plot_mpl.Plottable_USAXS_Dataset()
    ds_full.label = 'full data'
    ds_full.Q = scan.reduced['full']['Q']
    ds_full.I = scan.reduced['full']['R']

    ds_250 = plot_mpl.Plottable_USAXS_Dataset()
    ds_250.label = 'rebinned (250) data'
    ds_250.Q = scan.reduced['250']['Q']
    ds_250.I = scan.reduced['250']['R']

    pvwatch.logMessage( '  plotting to ' + plotfile )

    plot_mpl.livedata_plot(
        [ds_full, ds_250],
        plotfile,
        'test: ' + os.path.basename(hdf5_file)
        )
