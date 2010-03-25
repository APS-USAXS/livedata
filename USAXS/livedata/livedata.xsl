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
                <title>USAXS status</title>
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
                    <tr><td align="center" class="description">
                        <font color="white">USAXS status</font></td></tr>
                    <tr><td align="center"><font color="white">HTML page refresh interval 0:05:00 (h:mm:ss)</font></td></tr>
                    <tr bgcolor="lightblue">
                        <td align="center">
                            Webcam: <a href="http://usaxsqvs1.xor.aps.anl.gov">http://usaxsqvs1.xor.aps.anl.gov</a>
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
                                        <xsl:when test="//pv[@name='32idbUSX:pmm01:reg01:bo01']/value=1">
                                            <td bgcolor="#22ff22">USAXS CCD: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">USAXS CCD: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@name='32idbUSX:rmm02:reg01:bo08']/value=1">
                                            <td bgcolor="#22ff22">USAXS Ti filter: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">USAXS Ti filter: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@name='PA:32ID:A_SHTRS_CLOSED.VAL']/value=0">
                                            <td bgcolor="#22ff22">mono: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">mono: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@name='PA:32ID:B_SHTRS_CLOSED.VAL']/value=0">
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
                                        <xsl:when test="//pv[@name='S:SRcurrentAI']/value>2">
                                            <td bgcolor="#22ff22">
                                                <a  href="http://www.aps.anl.gov/aod/blops/plots/smallStatusPlot.png">
                                                APS current</a> = 
                                                <xsl:value-of select="//pv[@name='S:SRcurrentAI']/value"/> mA</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">
                                                <a  href="http://www.aps.anl.gov/aod/blops/plots/smallStatusPlot.png">
                                                    APS current</a> = 
                                                <xsl:value-of select="//pv[@name='S:SRcurrentAI']/value"/> mA</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <td>ID E = <xsl:value-of select="//pv[@name='ID32:Energy']/value"/> keV</td>
                                    <td>DCM E = <xsl:value-of select="//pv[@name='32ida:BraggEAO']/value"/> keV</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <tr>
                                    <td>|Q| = <xsl:value-of select="//pv[@name='32idbLAX:USAXS:Q']/value"/> 1/A</td>
                                    <td>I = <xsl:value-of select="//pv[@name='32idbLAX:USAXS:I']/value"/> pA/uA</td>
                                    <td>SAD = <xsl:value-of select="//pv[@name='32idbLAX:USAXS:SAD']/value"/> mm</td>
                                    <td>SDD = <xsl:value-of select="//pv[@name='32idbLAX:USAXS:SDD']/value"/> mm</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <td>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@name='32idbMIR:seq01:cr:inpos.RVAL']/value=1.0">
                                            <xsl:value-of select="//pv[@name='32idbMIR:seq01:cr:inpos.RVAL']/description"/>
                                        </xsl:when>
                                        <xsl:when test="//pv[@name='32idbMIR:seq01:rh:inpos.RVAL']/value=1.0">
                                            <xsl:value-of select="//pv[@name='32idbMIR:seq01:rh:inpos.RVAL']/description"/>
                                        </xsl:when>
                                        <xsl:when test="//pv[@name='32idbMIR:seq01:si:inpos.RVAL']/value=1.0">
                                            <xsl:value-of select="//pv[@name='32idbMIR:seq01:si:inpos.RVAL']/description"/>
                                        </xsl:when>
                                        <xsl:when test="//pv[@name='32idbMIR:seq01:wht:inpos.RVAL']/value=1.0">
                                            <xsl:value-of select="//pv[@name='32idbMIR:seq01:wht:inpos.RVAL']/description"/>
                                        </xsl:when>
                                        <xsl:otherwise>USAXS mirror not ready</xsl:otherwise>
                                    </xsl:choose>
                                    
                                </td>
                                <td>PF4 filter transmission: 
                                    <xsl:value-of select="//pv[@name='32idbUSX:pf4:trans']/value"/> 
                                    (Al=<xsl:value-of select="//pv[@name='32idbUSX:pf4:filterAl']/value"/> mm, 
                                    Ti=<xsl:value-of select="//pv[@name='32idbUSX:pf4:filterTi']/value"/> mm, 
                                    glass=<xsl:value-of select="//pv[@name='32idbUSX:pf4:filterGlass']/value"/> mm)
                                </td>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" bgcolor="bisque" class="description">
                            <xsl:value-of select="//pv[@name='32idbLAX:USAXS:sampleTitle']/value"/> 
                        </td>
                    </tr>
                    <tr>
                        <td align="center" bgcolor="lightblue">
                            <font SIZE="4">
                                <xsl:value-of select="//pv[@name='32idbLAX:USAXS:state']/value"/> 
                            </font>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <td align="left">spec macro: 
                                    <a href="specmacro.txt">
                                        <xsl:value-of select="//pv[@name='32idbLAX:string19']/value"/> 
                                    </a>
                                </td>
                                <td align="center">
                                    time stamp: 
                                    <xsl:value-of select="//pv[@name='32idbLAX:USAXS:timeStamp']/value"/>
                                </td>
                                <xsl:choose>
                                    <xsl:when test="//pv[@name='32idbLAX:bit19.VAL=1']/value>2">
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
                                    <xsl:value-of select="//pv[@name='32idbLAX:USAXS:userDir']/value"
                                    />/<xsl:value-of select="//pv[@name='32idbLAX:USAXS:specFile']/value"
                                    />
                                </td>
                                <td align="center">
                                    scan #<xsl:value-of select="//pv[@name='32idbLAX:USAXS:specScan']/value"/>
                                </td>
                                <td align="center">
                                    <xsl:value-of select="//pv[@name='32idbLAX:USAXS:specScan']/timestamp"/>
                                </td>
                            </table>
                        </td>
                    </tr>
                </table>
                
                <BR/>
                <h4>slits</h4>
                
                <table border="2">
                    <tr>
                        <td>slits</td>
                        <td>mm</td>
                        <td>mm</td>
                        <td>mm</td>
                        <td>mm</td>
                    </tr>
                    <tr>
                        <td>USAXS (h,v)(gap,center)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c3:m4.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c3:m3.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c3:m2.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c3:m1.RBV']/value"/></td>
                        
                    </tr>
                    <tr>
                        <td>white (r,l,t,b)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idb:m3.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idb:m1.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idb:m4.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idb:m2.RBV']/value"/></td>
                    </tr>
                </table>
                <table>
                    <tr>
                        
                        <td>
                            <h4>detectors</h4>
                            <table border="2">
                                <tr>
                                    <td>detector</td>
                                    <td>counts</td>
                                    <td>VDC</td>
                                    <td>gain,V/A</td>
                                    <td>current,A</td>
                                </tr>
                                
                                <tr>
                                    <td>I0</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbUSX:scaler1.S2']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbUSX:ath01:ana01:ai05.VAL']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbUSX:fem02:seq01:gain']/value"/></td>
                                    <td>-calculated term- not ready yet</td>
                                </tr>
                                <tr>
                                    <td>I00</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbUSX:scaler1.S3']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbUSX:ath01:ana01:ai06.VAL']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbUSX:fem03:seq01:gain']/value"/></td>
                                    <td>-calculated term- not ready yet</td>
                                </tr>
                                <tr>
                                    <td>I000</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbUSX:scaler1.S5']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbMIR:ath01:ana01:ai01.VAL']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbMIR:fem01:seq01:gain']/value"/></td>
                                    <td>-calculated term- not ready yet</td>
                                </tr>
                                <tr>
                                    <td>photodiode</td>
                                    <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbUSX:scaler1.S4']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbUSX:ath01:ana01:ai07.VAL']/value"/></td>
                                    <td><xsl:value-of select="//pv[@name='32idbUSX:fem01:seq01:gain']/value"/></td>
                                    <td>-calculated term- not ready yet</td>
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
                    <tr>
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
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c4:m1.RBV']/value"/></td>
                        <td><xsl:value-of select="//pv[@name='32idbLAX:mr:encoder']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c0:m6.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c0:m7.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    
                    <tr>
                        <td>ms</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c0:m8.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c0:m4.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c0:m5.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    <tr>
                        <td>s</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c2:m1.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c2:me.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    <tr>
                        <td>as</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c2:m8.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c1:m4.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c1:m5.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    
                    <tr>
                        <td>a</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c5:m1.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c1:m6.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c1:m7.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c1:m8.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    <tr>
                        <td>d</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c2:m4.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c2:m5.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    <tr>
                        <td>DCM theta</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32ida:m1.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    <tr>
                        
                        <td>mirror</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbMIR:m1.RBV']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbMIR:m2.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                    <tr>
                        <td>tcam</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@name='32idbLAX:m58:c0:m3.RBV']/value"/></td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                        <td bgcolor="#dddddd">&#160;</td>
                    </tr>
                </table>
                
                <br/>
                
                <hr/>
                
                <p><small>svn id: $ Id: $</small></p>
                
            </body>
            
        </html>
        
    </xsl:template>
    
</xsl:stylesheet>
