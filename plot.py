#!/usr/bin/env python
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################

'''
   read a SPEC data file and plot the last n USAXS scans for the livedata WWW page
'''

import os
import math
import time
import subprocess
import shlex
import shutil
import datetime		# date/time stamps
import prjPySpec	# read SPEC data files


PLOT_FORMAT = "png"
PLOTICUS = "/home/joule/USAXS/bin/pl"
PLOTFILE = "www/livedata.png"
SHELL_SCRIPT = "/tmp/plot-ploticus-usaxs.sh"


def update_n_plots(specFile, numScans):
    '''read the SPEC file and grab n scans'''
    sd = prjPySpec.specDataFile(specFile)
    scanList = []
    for scan in sd.scans:
        cmd = scan.scanCmd.split()[0]
	if (cmd == "uascan") or (cmd == "sbuascan"):
	    scanList.append(scan.scanNum)
	    if len(scanList) > numScans:
	        scanList.pop(0)
    if len(scanList) == 0:
    	return
    # extract the USAXS R(Q) profiles (ignoring error estimates)
    usaxs = []
    for scan in scanList:
        (title, qVec, rVec) = calc_usaxs_data(sd.scans[scan-1])
	entry = {}
	entry['scan'] = scan
	entry['title'] = title
	entry['qVec'] = qVec
	entry['rVec'] = rVec
	usaxs.append( entry )
    #---- format the data in the ploticus way
    (data_rows, qMin, qMax, iMin, iMax) = ploticus_data(usaxs)
    if len(data_rows) == 0:
        return
    # use temporary files with ploticus
    epoch = int(time.mktime(time.gmtime()))
    root = "%s-%d-%08x" % ("/tmp/ploticus", os.getpid(), epoch)
    tempDataFile = root + ".dat"
    tempPloticusFile = root + ".pl"
    tempPltFile = root + "." + PLOT_FORMAT
    #---- make the ploticus command script
    ploticus = {}
    ploticus['specFile'] = specFile
    ploticus['dataFile'] = tempDataFile
    ploticus['title'] = specFile
    ploticus['Qmin'] = 1e-5
    ploticus['Qmax'] = 1.0
    ploticus['Qmin'] = float(qMin)
    ploticus['Qmax'] = float(qMax)
    ploticus['Imin'] = float(iMin)
    ploticus['Imax'] = float(iMax)
    ploticus['scanList'] = ""
    for scan in usaxs:
        ploticus['scanList'] += "S" + str(int(scan['scan']))
	label = "S" + str(int(scan['scan'])) + scan['title']
	ploticus[label] = "#%d: %s" % (scan['scan'], scan['title'])
    command_script = ploticus_commands(ploticus, usaxs)
    #---- make the plot
    run_ploticus(command_script, data_rows, PLOTFILE)
    # perhaps copy the SPEC macro here, as well


def run_ploticus(script, data, plot):
    '''use ploticus to generate the plot image file'''
    #---- write the ploticus command script
    ext = os.extsep + "pl"
    (f, tmpScript) = tempfile.mkstemp(dir="/tmp", text=True, suffix=ext)
    f = open(tmpScript, "w")
    f.write("\n".join(script))
    f.close()
    #---- write the plot data file
    ext = os.extsep + "dat"
    (f, tmpData) = tempfile.mkstemp(dir="/tmp", text=True, suffix=ext)
    f = open(tmpData, "w")
    f.write("\n".join(data))
    f.close()
    #---- run ploticus
    ext = os.extsep + PLOT_FORMAT
    (f, tmpPlot) = tempfile.mkstemp(dir="/tmp", text=False, suffix=ext)
    command = "%s %s -%s -o %s" % (PLOTICUS, tmpScript, PLOT_FORMAT, tmpPlot)
    lex = shlex.split(command)
    p = subprocess.Popen(lex)
    p.wait()
    #---- copy and cleanup
    shutil.copy2(tmpFile, plot)
    os.remove(tmpScript)
    os.remove(tmpData)
    os.remove(tmpPlot)


def ploticus_commands(db, usaxs):
    '''plot USAXS data using ploticus'''
    output = []
    output.append("#proc page")
    output.append("  backgroundcolor: rgb(1.0,0.94,0.85)")
    output.append("")
    output.append("#proc annotate")
    output.append("  location:  1 0.45")
    output.append("  textdetails: align=L size=6")
    output.append("  text: APS/XSD USAXS data")
    output.append("")
    output.append("#proc annotate")
    output.append("  location:  1 0.35")
    output.append("  fromcommand: date")
    output.append("  textdetails: align=L size=6")
    output.append("")
    output.append("#proc getdata")
    output.append("  fieldnameheader: yes")
    output.append("  delim: whitespace")
    output.append("  commentchar: #")
    output.append("  file:  " + db['dataFile'])
    output.append("")
    output.append("#proc areadef ")
    output.append("  rectangle: 1 1 7 7")
    output.append("  areacolor: rgb(0.95,1.0,0.97)")
    output.append("  frame: color=rgb(0.2,0.2,0.1) width=3.0")
    output.append("  title: " + db['title'])
    output.append("  titledetails: align=C size=24")
    output.append("  xscaletype: log")
    output.append("  xrange: %.20f %.20f" % (db['Qmin'], db['Qmax']))
    output.append("  yscaletype: log")
    output.append("  yrange: %.30f %.30f" % (db['Imin'], db['Imax']))
    #output.append("  yautorange: datafield=3")
    output.append("")
    output.append("#proc xaxis ")
    output.append("  label: |Q|, 1/A ")
    output.append("  labeldetails: size=18")
    output.append("  selflocatingstubs: text")
    start = int(math.floor(math.log10(db['Qmin'])))
    finish = int(math.ceil(math.log10(db['Qmax'])))
    for y in range(start, finish+1):
	# major tick marks
	output.append("  1e%d 1e%d" % (y, y))
	for x in range(2, 10):
	    # minor tick marks
	    output.append("  %de%d" % (x, y))
    output.append("  #include $chunk_logtics")
    output.append("  stubrange:  %s %s" % (db['Qmin'], db['Qmax']))
    output.append("  grid: yes ")
    output.append("  grid color=grey(0.8)")
    output.append("")
    output.append("#proc yaxis ")
    output.append("  label: USAXS intensity, a.u. ")
    output.append("  labeldetails: size=18")
    output.append("  selflocatingstubs: text")
    start = int(math.floor(math.log10(db['Imin'])))
    finish = int(math.ceil(math.log10(db['Imax'])))
    for y in range(start, finish+1):
	# major tick marks
	output.append("  1e%d 1e%d" % (y, y))
	for x in range(2, 10):
	    # minor tick marks
	    output.append("  %de%d" % (x, y))
    output.append("  #include $chunk_logtics")
    output.append("  stubrange:  %s %s" % (db['Imin'], db['Imax']))
    output.append("  grid: yes")
    output.append("  grid color=grey(0.8)")
    output.append("")
    # ---
    symbolList = ("triangle", "diamond", "square", "downtriangle", "lefttriangle", "righttriangle")
    colorList = ("green", "purple", "blue", "black", "red")
    i = 0
    for scan in usaxs:
        if i+1 == len(usaxs):
	    # this is the most recent scan, make it the last color ("red")
	    color = colorList[-1]
	else:
	    color = colorList[i % len(colorList)]
	symbol = symbolList[i % len(symbolList)]
 	output.append("#proc lineplot ")
 	output.append("  xfield: 2")
 	output.append("  yfield: 3")
 	output.append("  linedetails: color=%s width=0.5" % color)
 	output.append("  pointsymbol: shape=%s radius=0.025 linecolor=%s fillcolor=white" % (symbol, color))
 	output.append("  legendlabel: %s" % scan['title'])
 	output.append("  select: @@dataset == S%d" % scan['scan'])
        output.append("")
	i += 1
    output.append("#proc rect")
    output.append("  rectangle: 4.2 5.7   6.8 6.8")
    output.append("  color: white")
    output.append("  bevelsize: 0.05")
    output.append("")
    output.append("#proc legend")
    output.append("  location: 4.5 6.7")
    output.append("  seglen: 0.2")
    output.append("  format: multiline")
    output.append("  textdetails: align=Right")
    return output


def ploticus_data(usaxs):
    '''build the data portion of the ploticus script'''
    qMin = None
    qMax = None
    iMin = None
    iMax = None
    result = []
    format = "%-10s %s %s"
    result.append("%-10s %15s %s" % ("dataset", "qVec", "rVec"))
    for scan in usaxs:
	# convert data columns to ordered-pairs
	pairs = zip(scan['qVec'], scan['rVec'])
	sLabel = "S" + str(int(scan['scan']))
	for (qStr, iStr) in pairs:
	    USAXS_Q = math.fabs(float(qStr))
	    USAXS_I = float(iStr)
	    if (USAXS_Q == 0) or (USAXS_I <= 0):
	        label = "ignore"
	    else:
	        label = S
		#--- initialize, if necessary
		if qMin == None:
		    qMin = USAXS_Q
		    qMax = USAXS_Q
		    iMin = USAXS_I
		    iMax = USAXS_I
		#--- update, if necessary
		if USAXS_Q < qMin:
		    qMin = USAXS_Q
		if USAXS_Q > qMax:
		    qMax = USAXS_Q
		if USAXS_I < iMin:
		    iMin = USAXS_I
		if USAXS_I > iMax:
		    iMax = USAXS_I
	    result.append("%-10s %15s %s" % (label, USAXS_Q, USAXS_I))
	# strange ploticus bug that will not plot any data when Qmax/Qmin < 2.9
	if qMax < 3*qMin:
	    #print "moving limits!"
	    # move limits symmetrically
	    qMax = qMin * 1.5
	    qMin = qMin / 1.5
	    #print qMin, qMax, iMin, iMax
    return result, qMin, qMax, iMin, iMax


def calc_usaxs_data(specScan):
    '''calculate the USAXS R wave from the raw SPEC scan data'''
    d2r = math.pi / 180
    sampleTitle = specScan.comments[0]
    arCenter = specScan.positioner['ar']
    wavelength = specScan.float['DCM_lambda']
    numData = len(specScan.data['Epoch'])
    USAXS_Q = []
    USAXS_I = []
    for i in range(numData):
	pd_counts = specScan.data['pd_counts'][i]
	pd_range = specScan.data['pd_range'][i]
	ar_enc = specScan.data['ar_enc'][i]
	seconds = specScan.data['seconds'][i]
	I0 = specScan.data['I0'][i]
	index = str(int(pd_range))
	diode_gain = specScan.float["UPD2gain" + index]
	dark_curr = specScan.float["UPD2bkg" + index]
	V_f_gain = 1e5
	#----
	qVec = (4 * math.pi / wavelength) * math.sin(d2r*(arCenter - ar_enc)/2)
	rVec = (pd_counts - seconds*dark_curr) / diode_gain / I0 / V_f_gain
	#----
	USAXS_Q.append( str(qVec) )
        USAXS_I.append( str(rVec) )
    return sampleTitle, USAXS_Q, USAXS_I


if __name__ == '__main__':
    specFile = '/share1/USAXS_data/2010-03/03_25.dat'
    numScans = 5
    update_n_plots(specFile, numScans)
