#!/usr/bin/env python

'''
receive a list of USAXS scans for the livedata WWW page and chart them with ploticus

@note: writes the chart locally, not to the WWW server
'''

import math
import os
import localConfig      # definitions for 15ID
import wwwServerTransfers

SYMBOL_LIST = ("triangle", "diamond", "square", "downtriangle", "lefttriangle", "righttriangle")
COLOR_LIST = ("green", "purple", "blue", "black", "orange") # red is NOT in the list

SCRIPT_FILE = 'livedata.pl'
CHART_FILE = 'livedata.png'


class Lineplot(object):
    '''holds data for one lineplot on the chart'''
    
    def __init__(self):
        self.title = 'data'
        self.x = []
        self.y = []
        self.label = []
        self.scan_key = ''


class Ploticus(object):
    '''representation of a Ploticus chart'''
    
    def __init__(self):
        self.tempDataFile = None
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.title = 'ploticus chart'
        self.subtitle = 'demonstration'
        self.data = []
    
    def addCurve(self, scan):
        '''add one scan (curve) to the chart'''
        pairs = zip(scan.qVec, scan.rVec)     # convert arrays to ordered pairs
        if len(pairs) == 0:
            return
        scan_key = 'S' + str(scan.number)
        self.title = scan.file
        lineplot = Lineplot()
        lineplot.title = scan.title
        lineplot.scan_key = scan_key
        for x, y in pairs:
            x = math.fabs(float(x))
            y = float(y)

            if (x == 0) or (y <= 0):
                label = "ignore"
            else:
                label = scan_key
                #--- initialize, if necessary
                if self.xmin == None:
                    self.xmin = self.xmax = x
                    self.ymin = self.ymax = y
                #--- update, if necessary
                if x < self.xmin: self.xmin = x
                if x > self.xmax: self.xmax = x
                if y < self.ymin: self.ymin = y
                if y > self.ymax: self.ymax = y
            lineplot.x.append(x)
            lineplot.y.append(y)
            lineplot.label.append(label)

        self.data.append(lineplot)
    
    def create(self, chartfile = CHART_FILE):
        '''create the PNG chart of the USAXS scans'''
        # build the ploticus script
        t = self._build()
        
        # write the script to a file
        f = open(SCRIPT_FILE, 'w')
        f.write(t)
        f.close()
        
        # run ploticus
        os.environ['PLOTICUS_PREFABS'] = localConfig.PLOTICUS_PREFABS
        command = "%s -%s %s -o %s" % (localConfig.PLOTICUS, localConfig.PLOT_FORMAT,
                       SCRIPT_FILE, chartfile)
        wwwServerTransfers.execute_command(command)
    
    def _build(self):
        s = self._header()
        s += self._areadef()
        s += self._xaxis()
        s += self._yaxis()
        s += self._lineplot()
        s += self._legend()
        s += self._trailer()
        return s
    
    def _header(self):
        return u'''
#proc page
    backgroundcolor: rgb(1.0,0.94,0.85)

#proc annotate
    location:  1 0.45
    textdetails: align=L size=6
    text: APS/XSD USAXS data

#proc annotate
    location:  1 0.35
    fromcommand: date
    textdetails: align=L size=6

#proc getdata
    #intrailer
        '''
       
    def _areadef(self):
        t =  "\n#proc areadef "
        t += "\n  rectangle: 1 1 7 7"
        t += "\n  areacolor: rgb(0.95,1.0,0.97)"
        t += "\n  frame: color=rgb(0.2,0.2,0.1) width=3.0"
        t += "\n  title: " + self.title
        t += "\n  titledetails: align=C size=24"
        t += "\n  xscaletype: log"
        t += "\n  xrange: %.20f %.20f" % (self.xmin, self.xmax)
        t += "\n  yscaletype: log"
        t += "\n  yrange: %.30f %.30f" % (self.ymin, self.ymax)
        t += "\n"
        #output.append("  yautorange: datafield=3")
        return t
    
    def _tick_marks(self, start, finish):
        t = ''
        for y in range(start, finish+1):
            # major tick marks
            t += "\n  1e%d 1e%d" % (y, y)
            for x in range(2, 10):
                # minor tick marks
                t += "\n  %de%d" % (x, y)
        return t

    def _xaxis(self):
        t = ''
        t += "\n#proc xaxis "
        t += "\n  label: |Q|, 1/A "
        t += "\n  labeldetails: size=18"
        t += "\n  selflocatingstubs: text"
        
        # plot no lower than Q=1e-6, even if Qmin smaller
        start = max(-6, int(math.floor(math.log10(self.xmin))))
        finish = int(math.ceil(math.log10(self.xmax)))
        t += self._tick_marks(start, finish)
        
        t += "\n  #include $chunk_logtics"
        t += "\n  stubrange:  %s %s" % (self.xmin, self.xmax)
        t += "\n  grid: yes "
        t += "\n  grid color=grey(0.8)"
        t += "\n"
        return t
    
    def _yaxis(self):
        t = ''
        t += "\n#proc yaxis "
        t += "\n  label: USAXS intensity, a.u. "
        t += "\n  labeldetails: size=18"
        t += "\n  selflocatingstubs: text"
        
        start = int(math.floor(math.log10(self.ymin)))
        finish = int(math.ceil(math.log10(self.ymax)))
        t += self._tick_marks(start, finish)

        t += "\n  #include $chunk_logtics"
        t += "\n  stubrange:  %s %s" % (self.ymin, self.ymax)
        t += "\n  grid: yes"
        t += "\n  grid color=grey(0.8)"
        t += "\n"
        return t
    
    def _lineplot(self):
        t = ''
        i = -1
        for lineplot in self.data:
            i += 1
            if i+1 == len(self.data):
                color = 'red'
            else:
                color = COLOR_LIST[i % len(COLOR_LIST)]
            symbol = SYMBOL_LIST[i % len(SYMBOL_LIST)]
            label = lineplot.scan_key + ': ' + lineplot.title
            t +=  '\n#proc lineplot '
            t += '\n  xfield: 2'
            t += '\n  yfield: 3'
            t += "\n  linedetails: color=%s width=0.5" % color
            t += "\n  pointsymbol: shape=%s radius=0.025 linecolor=%s fillcolor=white" % (symbol, color)
            t += "\n  legendlabel: %s" % label
            t += "\n  select: @@dataset == %s" % lineplot.scan_key
            t += '\n'
        return t
    
    def _legend(self):
        return u'''
#proc rect
    rectangle: 1.2 1.2   3.8 2.2
    color: white
    bevelsize: 0.05

#proc legend
    location: 1.5 2.15
    seglen: 0.2
    format: multiline
    textdetails: align=Right
        '''
       
    def _trailer(self):
        '''add the USAXS scan data to the ploticus script'''
        t = u'''
#proc trailer
  fieldnameheader: yes
  delim: whitespace
  data:
    dataset        qVec        rVec'''
        for lineplot in self.data:
            sets = zip(lineplot.label, lineplot.x, lineplot.y)
            for label, x, y in sets:
                t += "\n    %-10s %15s %s" % (label, x, y)
        return t


if __name__ == '__main__':
    import plot
    numScans = 5
    scans = plot.identify_last_n_scans(numScans)
    plot.get_spec_data()
    pl = Ploticus()
    for scan in scans:
        pl.addCurve(scan)
    pl.create()


########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
