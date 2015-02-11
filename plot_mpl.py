#!/usr/bin/env python

'''use MatPlotLib for the USAXS livedata and generic SPEC scan plots'''


import datetime
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt
import numpy as np

BISQUE_RGB    = (255./255, 228./255, 196./255)  # 255 228 196 bisque
MINTCREAM_RGB = (245./255, 255./255, 250./255)  # 245 255 250 MintCream

SYMBOL_LIST = ("^", "D", "s", "v", "<", ">")
COLOR_LIST = ("green", "purple", "blue", "black", "orange") # red is NOT in the list

CHART_FILE = 'livedata.png'

# MatPlotLib advises to re-use the figure() object rather create new ones
# http://stackoverflow.com/questions/21884271/warning-about-too-many-open-figures
LIVEDATA_PLOT_FIG = plt.figure(figsize=(7.5, 8), dpi=300)
SPEC_PLOT_FIG = plt.figure(figsize=(9, 5))


class Plottable_USAXS_Dataset(object):
    Q = None
    I = None
    label = None


def livedata_plot(datasets, plotfile, title=None):
    '''
    generate the USAXS livedata plot
    
    :param [Plottable_USAXS_Dataset] datasets: USAXS data to be plotted, newest data last
    :param str plotfile: file name to write plot image
    '''
    fig = LIVEDATA_PLOT_FIG

    ax = fig.add_subplot('111', axisbg=MINTCREAM_RGB)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$|\vec{Q}|, 1/\AA$')
    ax.set_ylabel(r'Raw Intensity ($R(|\vec{Q}|)$), a.u.')
    ax.grid(True, which='both')

    legend_handlers = {}  # to configure legend for one symbol per dataset
    for i, ds in enumerate(datasets):
        if i < len(datasets)-1:
            color = COLOR_LIST[i % len(COLOR_LIST)]
            symbol = SYMBOL_LIST[i % len(SYMBOL_LIST)]
        else:
            color = 'red'
            symbol = 'o'
        pl, = ax.plot(ds.Q, ds.I, symbol, label=ds.label, mfc='w', mec=color, ms=3, mew=1)
    legend_handlers[pl] = matplotlib.legend_handler.HandlerLine2D(numpoints=1)

    timestamp_str = 'APS/XSD USAXS: ' + str(datetime.datetime.now())
    if title is None:
        title = timestamp_str
    else:
        fig.text(0.02, 0., timestamp_str,
            fontsize=8, color='gray',
            ha='left', va='bottom', alpha=0.5)
    plt.title(title, fontsize=12)
    plt.legend(loc='lower left', fontsize=10, handler_map=legend_handlers)
    plt.savefig(plotfile, bbox_inches='tight', facecolor=BISQUE_RGB)


def spec_plot(x, y, 
              plotfile, 
              title=None, subtitle=None, 
              xtitle=None, ytitle=None, 
              xlog=False, ylog=False,
              timestamp_str=None):
    '''
    generate a plot of a scan from a SPEC file
    
    :param [float] x: horizontal axis data
    :param [float] y: vertical axis data
    :param str plotfile: file name to write plot image
    :param str xtitle: horizontal axis label (default: not shown)
    :param str ytitle: vertical axis label (default: not shown)
    :param str title: title for plot (defaults to date time)
    :param bool xlog: should X axis be log (defaults to False=linear)
    :param bool ylog: should Y axis be log (defaults to False=linear)
    :param str timestamp_str: date to use on plot (defaults to now)
    '''
    fig = SPEC_PLOT_FIG
    fig.clf()

    ax = fig.add_subplot('111')
    if xlog:
        ax.set_xscale('log')
    if ylog:
        ax.set_yscale('log')
    if not xlog and not ylog:
        ax.ticklabel_format(useOffset=False)
    if xtitle is not None:
        ax.set_xlabel(xtitle)
    if ytitle is not None:
        ax.set_ylabel(ytitle)

    pl = ax.plot(x, y, 'o-')
    if subtitle is not None:
        plt.title(subtitle, fontsize=9)

    if timestamp_str is None:
        timestamp_str = str(datetime.datetime.now())
    if title is None:
        title = timestamp_str
    else:
        fig.text(0.02, 0., timestamp_str,
            fontsize=8, color='gray',
            ha='left', va='bottom', alpha=0.5)
    plt.suptitle(title, fontsize=10)
    plt.savefig(plotfile, bbox_inches='tight')


def main():
    '''demo of this code'''
    x = np.arange(0.105, 2*np.pi, 0.01)
    ds1 = Plottable_USAXS_Dataset()
    ds1.Q = x
    ds1.I = np.sin(x**2) * np.exp(-x) + 1.0e-5
    ds1.label = 'sin(x^2) exp(-x)'
    
    ds2 = Plottable_USAXS_Dataset()
    ds2.Q = x
    ds2.I = ds1.I**2 + 1.0e-5
    ds2.label = '$[\sin(x^2)\cdot\exp(-x)]^2$'
    
    ds3 = Plottable_USAXS_Dataset()
    ds3.Q = x
    ds3.I = np.sin(5*x) / (5*x)  + 1.0e-5
    ds3.label = 'sin(5x)/(5x)'
    
    ds4 = Plottable_USAXS_Dataset()
    ds4.Q = x
    ds4.I = ds3.I**2 + 1.0e-5
    ds4.label = r'$[\sin(5x)/(5x)]^2$'
    
    livedata_plot([ds2, ds4], CHART_FILE)


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
