#!/usr/bin/env python

'''use MatPlotLib for the USAXS livedata and generic SPEC scan plots'''


import datetime
import logging
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np


logger = logging.getLogger(__name__)

BISQUE_RGB    = (255./255, 228./255, 196./255)  # 255 228 196 bisque
MINTCREAM_RGB = (245./255, 255./255, 250./255)  # 245 255 250 MintCream

SYMBOL_LIST = ("^", "D", "s", "v", "d", "<", ">")
COLOR_LIST = "orange salmon lime green blue purple violet chocolate gray black".split() # red is NOT in the list

CHART_FILE = 'livedata.png'


class PlotException(Exception):
    """one of the plot traces has raised an excpetion"""


# MatPlotLib has several interfaces for plotting
# Since this module runs as part of a background job generating lots of plots,
# the standard plt code is not the right model.  It warns after 20 plots
# and will eventually run out of memory.  Here's the fix used in this module:
# http://stackoverflow.com/questions/16334588/create-a-figure-that-is-reference-counted/16337909#16337909

class Plottable_USAXS_Dataset(object):
    '''data model for the plots below'''
    Q = None
    I = None
    label = None


def livedata_plot(datasets, plotfile, title=None):
    '''
    generate the USAXS livedata plot

    :param [Plottable_USAXS_Dataset] datasets: USAXS data to be plotted, newest data last
    :param str plotfile: file name to write plot image
    '''
    fig = matplotlib.figure.Figure(figsize=(7.5, 8), dpi=300)
    fig.clf()

    try:
        ax = fig.add_subplot('111', axisbg=MINTCREAM_RGB)
    except AttributeError:
        ax = fig.add_subplot('111', facecolor=MINTCREAM_RGB)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$|\vec{Q}|, 1/\AA$')
    ax.set_ylabel(r'$R(|\vec{Q}|)$, Raw Intensity, a.u.')
    ax.grid(True)

    timestamp_str = 'APS/XSD USAXS: ' + str(datetime.datetime.now())
    fig.suptitle(timestamp_str, fontsize=10)
    if title is not None:
        ax.set_title(title, fontsize=12)

    legend_handlers = {}  # to configure legend for one symbol per dataset
    faults = []
    for i, ds in enumerate(datasets):
        try:
            if i < len(datasets)-1:
                color = COLOR_LIST[i % len(COLOR_LIST)]
                symbol = SYMBOL_LIST[i % len(SYMBOL_LIST)]
            else:
                color = 'red'
                symbol = 'o'
            if ds.label.find('(fly)') >= 0:
                label = ds.label[:ds.label.find('(fly)')] + '(USAXS)'
            elif ds.label.find('(SAXS)') >= 0:
                label = ds.label[:ds.label.find('(SAXS)')] + '(SAXS)'
            else:
                label = ds.label
            p = label.find(" ")
            if label.startswith("S") and p > 0:
                label = label[p:].strip()  # remove the scan number
            pl, = ax.plot(ds.Q, ds.I, symbol, label=label, mfc='w', mec=color, ms=3, mew=1)
            legend_handlers[pl] = matplotlib.legend_handler.HandlerLine2D(numpoints=1)
        except Exception as exc:
            faults.append((i, ds, exc))

    # ax.legend(loc='lower left', fontsize=9, handler_map=legend_handlers)  # the old way
    ax.legend(fontsize=8, handler_map=legend_handlers)
    # fig.tight_layout()  # does not look good, crowds the title
    FigureCanvas(fig).print_figure(plotfile, bbox_inches='tight', facecolor=BISQUE_RGB)
    if len(faults) > 0:
        fault_text = "\n".join(["{}".format(f) for f in faults])
        raise PlotException(fault_text)


def spec_plot(x, y,
              plotfile,
              title=None, subtitle=None,
              xtitle=None, ytitle=None,
              xlog=False, ylog=False,
              timestamp_str=None):
    '''
    generate a plot of a scan (as if data from a scan in a SPEC file)

    :param [float] x: horizontal axis data
    :param [float] y: vertical axis data
    :param str plotfile: file name to write plot image
    :param str xtitle: horizontal axis label (default: not shown)
    :param str ytitle: vertical axis label (default: not shown)
    :param str title: title for plot (default: date time)
    :param str subtitle: subtitle for plot (default: not shown)
    :param bool xlog: should X axis be log (default: False=linear)
    :param bool ylog: should Y axis be log (default: False=linear)
    :param str timestamp_str: date to use on plot (default: now)
    '''
    fig = matplotlib.figure.Figure(figsize=(9, 5))
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

    if subtitle is not None:
        ax.set_title(subtitle, fontsize=9)

    if timestamp_str is None:
        timestamp_str = str(datetime.datetime.now())
    if title is None:
        title = timestamp_str
    else:
        fig.text(0.02, 0., timestamp_str,
            fontsize=8, color='gray',
            ha='left', va='bottom', alpha=0.5)
    fig.suptitle(title, fontsize=10)

    ax.plot(x, y, 'o-')

    FigureCanvas(fig).print_figure(plotfile, bbox_inches='tight')


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
