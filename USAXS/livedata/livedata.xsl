<?xml version="1.0" encoding="UTF-8"?>
<!-- 
    ########### SVN repository information ###################
    # $Date$
    # $Author$
    # $Revision$
    # $URL$
    # $Id$
    ########### SVN repository information ###################
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    
    <xsl:template match="/">

        <html>
            <head>
                <meta http-equiv="Pragma" content="no-cache"/>
                <meta http-equiv="Refresh" content="300"/>
                <title>USAXS: status</title>
                <style type="text/css">
                    
                    body {
                        font: x-small Verdana, Arial, Helvetica, sans-serif; 
                    }
                    h1 {
                       font-size: 145%; 
                       margin-bottom: .5em; 
                    }
                    h2 {
                       font-size: 125%;
                       margin-top: 1.5em;
                       margin-bottom: .5em; 
                    }
                    h3 {
                        font-size: 115%;
                        margin-top: 1.2em;
                        margin-bottom: .5em
                    }
                    h4 {
                        font-size: 100%;
                       margin-top: 1.2em;
                       margin-bottom: .5em; 
                    }
                    p {
                      font: x-small Verdana, Arial, Helvetica, sans-serif;
                      color: #000000; 
                    }
                    .description {  
                        font-weight: bold; 
                        font-size: 150%;
                    }
                    td {
                        font-size: x-small; 
                    }
                    
                    li {
                        margin-top: .75em;
                        margin-bottom: .75em; 
                    }
                    ul {   
                        list-style: disc; 
                    }
                    
                    ul ul, ol ol , ol ul, ul ol {
                      margin-top: 1em;
                      margin-bottom: 1em; 
                    }
                    li p {
                      margin-top: .5em;
                      margin-bottom: .5em; 
                    }
                    
                    .dt {
                        margin-bottom: -1em; 
                    }
                    .indent {
                        margin-left: 1.5em; 
                    }
                    sup {
                       text-decoration: none;
                       font-size: smaller; 
                    }
                    
                </style>
            </head>
            <body>
                
                <table border="0" width="96%" rules="none" bgcolor="darkblue">
                    <tr>
			<td align="center" class="description">
 			    <font color="white">USAXS status</font>
			</td>
		    </tr>
                    <tr>
		        <td align="center">
			    <font color="white">HTML page refresh interval 0:05:00 (h:mm:ss)</font>
			</td>
		    </tr>
                    <tr bgcolor="lightblue">
                        <td align="center">
                            Webcam: 
			    <a href="http://usaxsqvs1.xor.aps.anl.gov">
			        http://usaxsqvs1.xor.aps.anl.gov
			    </a>
                        </td>
                    </tr>
                    <tr bgcolor="lightblue">
                        <td align="center">
                            <font>
                                <em>
                                    <a href="raw-report.html">raw</a> | 
				    <!--
                                    / 
                                    <a href="status.txt">descriptive</a>
                                    / -->
                                    <a href="http://usaxs.xor.aps.anl.gov/livedata/scanLog/scanlog.xml">scan log</a>
                                    content updated:
                                    <xsl:value-of select="/usaxs_pvs/datetime"/>
                                </em>
                            </font>
                        </td>
                    </tr>
                </table>
                <table border="1" width="96%" rules="all">
                    <tr>
                        <td>
                            <table border="1" width="100%" rules="all">
                                <tr>
                                    <td>shutters:</td>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='CCD_shtr_closed']/value=1">
                                            <td bgcolor="#22ff22">USAXS CCD: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">USAXS CCD: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='Ti_shtr_open']/value=1">
                                            <td bgcolor="#22ff22">USAXS Ti filter: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">USAXS Ti filter: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='mono_shtr_closed']/value=0">
                                            <td bgcolor="#22ff22">mono: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">mono: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='white_shtr_closed']/value=0">
                                            <td bgcolor="#22ff22">white: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">white: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <tr>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='SR_current']/value>2">
                                            <td bgcolor="#22ff22">
                                                <a href="http://www.aps.anl.gov/aod/blops/plots/smallStatusPlot.png">
                                                APS current</a> = 
                                                <xsl:value-of select="//pv[@id='SR_current']/value"/> mA</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">
                                                <a href="http://www.aps.anl.gov/aod/blops/plots/smallStatusPlot.png">
                                                    APS current</a> = 
                                                <xsl:value-of select="//pv[@id='SR_current']/value"/> mA</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <td>ID E = <xsl:value-of select="//pv[@id='Und_E']/value"/> keV</td>
                                    <td>DCM E = <xsl:value-of select="//pv[@id='DCM_E']/value"/> keV</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <tr>
                                    <td>|Q| = <xsl:value-of select="//pv[@id='USAXS_Q']/value"/> 1/A</td>
                                    <td>I = <xsl:value-of select="//pv[@id='USAXS_I']/value"/> pA/uA</td>
                                    <td>SAD = <xsl:value-of select="//pv[@id='SAD']/value"/> mm</td>
                                    <td>SDD = <xsl:value-of select="//pv[@id='SDD']/value"/> mm</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <td>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='mirror_cr_pos']/value=1.0">
                                            <xsl:value-of select="//pv[@id='mirror_cr_pos']/description"/>
                                        </xsl:when>
                                        <xsl:when test="//pv[@id='mirror_si_pos']/value=1.0">
                                            <xsl:value-of select="//pv[@id='mirror_si_pos']/description"/>
                                        </xsl:when>
                                        <xsl:when test="//pv[@id='mirror_rh_pos']/value=1.0">
                                            <xsl:value-of select="//pv[@id='mirror_rh_pos']/description"/>
                                        </xsl:when>
                                        <xsl:when test="//pv[@id='mirror_wh_pos']/value=1.0">
                                            <xsl:value-of select="//pv[@id='mirror_wh_pos']/description"/>
                                        </xsl:when>
                                        <xsl:otherwise>USAXS mirror not ready</xsl:otherwise>
                                    </xsl:choose>
                                    
                                </td>
                                <td>PF4 filter transmission: 
                                    <xsl:value-of select="//pv[@id='pf4_trans']/value"/> 
                                    (Al=<xsl:value-of select="//pv[@id='pf4_thickness_Al']/value"/> mm, 
                                    Ti=<xsl:value-of select="//pv[@id='pf4_thickness_Ti']/value"/> mm, 
                                    glass=<xsl:value-of select="//pv[@id='pf4_thickness_Gl']/value"/> mm)
                                </td>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" bgcolor="bisque" class="description">
                            <xsl:value-of select="//pv[@id='sampleTitle']/value"/> 
                        </td>
                    </tr>
                    <tr>
                        <td align="center" bgcolor="lightblue">
                            <font SIZE="4">
                                <xsl:value-of select="//pv[@id='state']/value"/> 
                            </font>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <td align="left">spec macro: 
                                    <a href="specmacro.txt">
                                        <xsl:value-of select="//pv[@id='spec_macro_file']/value"/> 
                                    </a>
                                </td>
                                <td align="center">
                                    time stamp: 
                                    <xsl:value-of select="//pv[@id='timeStamp']/value"/>
                                </td>
                                <xsl:choose>
                                    <xsl:when test="//pv[@id='USAXS_collecting']/value=1">
                                        <td bgcolor="#22ff22">USAXS scan running</td>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <td>not scanning USAXS</td>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <td align="left">
                                    <xsl:value-of select="//pv[@id='spec_dir']/value"
                                    />/<xsl:value-of select="//pv[@id='spec_data_file']/value"
                                    />
                                </td>
                                <td align="center">
                                    scan #<xsl:value-of select="//pv[@id='spec_scan']/value"/>
                                </td>
                                <td align="center">
                                    <xsl:value-of select="//pv[@id='spec_scan']/timestamp"/>
                                </td>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <BR/>
                <h4>slits</h4>
                
                <table border="2">
                    <tr style="background-color: grey; color: white;">
                        <td>slits</td>
                        <td>mm</td>
                        <td>mm</td>
                        <td>mm</td>
                        <td>mm</td>
                    </tr>
                    <tr>
                        <td>USAXS (h,v)(gap,center)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslith']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslitv']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslith0']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslitv0']/value"/></td>
                        
                    </tr>
                    <tr>
                        <td>white (r,l,t,b)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='wslitr']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='wslitl']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='wslitt']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='wslitb']/value"/></td>
                    </tr>
                </table>
                <table>
                    <tr>
                        
                        <td>
                            <h4>detectors</h4>
                            <table border="2">
                                <tr style="background-color: grey; color: white;">
                                    <td>detector</td>
                                    <td>counts</td>
                                    <td>VDC</td>
                                    <td>gain,V/A</td>
                                    <td>current,A</td>
                                </tr>
                                
                                <tr>
                                    <td>I0</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@id='scaler_I0']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I0_VDC']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I0_amp_gain']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I0_amp_current']/value"/></td>
                                </tr>
                                <tr>
                                    <td>I00</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@id='scaler_I00']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I00_VDC']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I00_amp_gain']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I00_amp_current']/value"/></td>
                                </tr>
                                <tr>
                                    <td>I000</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@id='scaler_I000']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I000_VDC']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I000_amp_gain']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='I000_amp_current']/value"/></td>
                                </tr>
                                <tr>
                                    <td>photodiode</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@id='scaler_diode']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='diode_VDC']/value"/></td>
                                    <td><xsl:value-of select="//pv[@id='diode_amp_gain']/value"/></td>
                                    <td>
				        <!--
					<xsl:value-of select="//pv[@id='diode_amp_current']/value"/>
					<br />
					-->
				        <xsl:value-of select="//pv[@id='diode_current']/value"/>
				    </td>
                                </tr>
                            </table>
                        </td>
                        
                        <td>
                            <h4>USAXS plot</h4>
                            <a href="showplot.html"><img SRC="livedata.png" ALT="plot of USAXS data" WIDTH="200"/></a>
                        </td>
                    </tr>
                </table>

                <h4>motors</h4>
                <table border="2">
                    <tr style="background-color: grey; color: white;">
                        <td>stage</td>
                        <td>rot,deg</td>
                        <td>encoder,deg</td>
                        <td>X,mm</td>
                        <td>Y,mm</td>
                        <td>Z,mm</td>
                        <td>tilt,deg</td>
                    </tr>
                    <tr>
                        <td>m</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mr']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mr_enc']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mx']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='my']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    
                    <tr>
                        <td>ms</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='msr']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='msx']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='msy']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mst']/value"/></td>
                    </tr>
                    <tr>
                        <td>s</td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='sx']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='sy']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    <tr>
                        <td>as</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='asr']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='asx']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='asy']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='ast']/value"/></td>
                    </tr>
                    
                    <tr>
                        <td>a</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='ar']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='ax']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='ay']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='az']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    <tr>
                        <td>d</td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='dx']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='dy']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    <tr>
                        <td>DCM theta</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='DCM_theta']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    <tr>
                        
                        <td>mirror</td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mirr_x']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mirr_vs']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    <tr>
                        <td>tcam</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='tcam']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                </table>
                
                <br/>
                
                <hr/>
                
                <p><small>svn id: $Id$</small></p>
                
            </body>
            
        </html>
        
    </xsl:template>
    
</xsl:stylesheet>
