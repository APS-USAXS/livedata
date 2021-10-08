
'''developer routine to test reduceFlyData.py'''

import os
import sys

import plot_mpl
import reduceFlyData
import pvwatch

# sys.argv = [sys.argv[0],]
#sys.argv.append( '-h' )
#sys.argv.append( '-V' )
sys.argv.append( '--recompute-full' )
sys.argv.append( '--recompute-rebinned' )


# test_files = glob.glob('testdata/flyscan_modes/*.h5')
# test_files = glob.glob('testdata/flyscan_modes/S18_FS_Fixed*.h5')    # from day with no beam, this dataset has problems!
# test_files = glob.glob('testdata/flyscan_modes/*_PSO_Fixed*.h5')     # from day with no beam
# test_files = glob.glob('testdata/flyscan_modes/S39_Blank*.h5')       # 2014-08-13, fly scan mode=1
# test_files = glob.glob('testdata/flyscan_modes/S44_GC_Adam*.h5')     # 2014-08-13, fly scan mode=1
# test_files = glob.glob('testdata/flyscan_modes/S19_FS_Fixed*.h5')
# test_files = glob.glob('testdata/fly/08_14_NIST_TRIP_fly/S48*.h5')
# test_files = glob.glob('testdata/fly/10_09_Prisk_fly/S5_Glass_Blank.h5')
# test_files = glob.glob('testdata/fly/10_09_Prisk2D1_fly/S*.h5')
# test_files = glob.glob('/share1/USAXS_data/2015-02/02_22_StressTest12keV_fly/S10*_*.h5')
# test_files = glob.glob('testdata/2015-02-24-flyScan/S*.h5')
# test_files = glob.glob('testdata/S*.h5')
# test_files = glob.glob('/share1/USAXS_data/2015-12/12_2_Kariuki_fly/S28_TestAmplifierA.h5')
# test_files = glob.glob('testdata/2016-02-10-USAXS/02_10_myers1_fly/S*_Glassy*.h5')
# test_files = ['/share1/USAXS_data/2016-08/08_02_GlassyCarbon_fly/GlassyCarbon_U_1_Time120s_0056.h5',]
test_files = ["/share1/USAXS_data/2021-10/10_05_Gadikota/10_05_Gadikota_usaxs/AAM_50mM_CaCO3_206min_1039.h5", ]

argv = list(sys.argv)

for hdf5_file in test_files:
    sys.argv = list(argv)
    sys.argv.append( hdf5_file )
    path = os.path.dirname(hdf5_file)
    scan = reduceFlyData.command_line_interface()

    plotfile = os.path.join(path, 'test_reduceFly__' + os.path.basename(hdf5_file) + '_.png')

    plot_mpl.spec_plot(
        scan.reduced['full']['Q'], scan.reduced['full']['R'],
        plotfile,
        xtitle='Q', ytitle='R',
        ylog=True,
        )

    plotfile = os.path.join(path, 'test_reduceFly_USAXS_' + os.path.basename(hdf5_file) + '_.png')
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
