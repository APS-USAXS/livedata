<?xml version="1.0" encoding="UTF-8"?>
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
                            <table border="1" width="100%" rules="all" bgcolor="lightblue">
                                <tr>
                                    <td>
					content updated:
 					<xsl:value-of select="/usaxs_pvs/datetime"/>
				    </td>
                                    <td align="center"><a href="raw-report.html">raw info</a> </td>
                                    <td align="center">scan log:
				        <a href="scanpager.php?pageID=99999">paged</a>
					|
				        <a href="scanlog.xml">full</a>
				    </td>
                                    <td align="center"><a href="specplots">SPEC plots</a></td>
                                    <td align="center"><a href="usaxstv.html">iPad/TV view</a></td>
                                    <td align="center"><a href="https://s9pva.xray.aps.anl.gov/cgi-bin/pvarch/show.py">PV watch</a></td>
				</tr>
                            </table>
                        </td>
                    </tr>
                    <tr bgcolor="lightblue">
		                <td>
                            <table border="1" width="100%" rules="all" bgcolor="lightblue">
                                <tr>
                                    <td>webcams</td>
                                    <!--
                axis server     164.54.143.40   axis-server.xray.aps.anl.gov
                164.54.143.41
                164.54.143.42
                164.54.143.43
                164.54.143.45
                164.54.143.46
                164.54.143.47
                                      -->
                    		    <td align="center">
                    		        <a href="http://axis-server.xray.aps.anl.gov">
                    		            Axis Server
                    		        </a>
                    		    </td>
                    		    <td align="center">
                    		        <a href="http://164.54.143.43">
                    		            Front table
                    		        </a>
                    		    </td>
                   		    <td align="center">
                    		        <a href="http://164.54.143.41">
                    		            A stage table
                    		        </a>
                    		    </td>
                   		    <td align="center">
                    		        <a href="http://164.54.143.42">
                    		            Side wall
                    		        </a>
                    		    </td>
                   		    <td align="center">
                    		        <a href="http://164.54.143.45">
                    		            Back table
                    		        </a>
                    		    </td>
                    		    <td align="center">
                    		        <a href="http://164.54.143.46">
                    		            Back wall
                    		        </a>
                    		    </td>
	               		    <td align="center">
                    		        <a href="http://164.54.143.47">
                    		            Left side table
                    		        </a>
                    		    </td>
                                </tr>
                            </table>
                            <table border="1" width="100%" rules="all" bgcolor="lightblue">
                                <tr>
                                    <td>webcams Beamline</td>
                                    <!--
 					Cryo system view
					http://urania.xray.aps.anl.gov/home/homeS.html
					Mono system view
					http://melpomene.xray.aps.anl.gov/home/homeS.html
					SOE
					http://clio.xray.aps.anl.gov/home/homeS.html
					need java, will run on Safari but not on Firefox on OSX
                                    -->
                    		    <td align="center">
                    		        <a href="http://urania.xray.aps.anl.gov/home/homeS.html">
                    		            Cryo system
                    		        </a>
                    		    </td>
                    		    <td align="center">
                    		        <a href="http://melpomene.xray.aps.anl.gov/home/homeS.html">
                    		            Monochromator
                    		        </a>
                    		    </td>
                    		    <td align="center">
                    		        <a href="http://clio.xray.aps.anl.gov/home/homeS.html">
                    		            SOE
                    		        </a>
                    		    </td>
                                 </tr>
                            </table>
                    	</td>
                    </tr>
                </table>
                <table border="1" width="96%" rules="all">
                    <tr>
                        <td>
                            <table border="1" width="100%" rules="all" bgcolor="mintcream">
                                <tr>
                                    <td>shutters:</td>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='CCD_shutter']/value=1">
                                            <td bgcolor="#ff2222">USAXS CCD: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td>USAXS CCD: closed</td><!-- no background color in this case -->
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                    <!--
                                        Ti shutter PV is:
                                        9idb:BioEnc2B3 with open being 1 (up), closed 0 (down)
                                     -->
                                        <xsl:when test="//pv[@id='Ti_shutter']/value=1">
                                            <td bgcolor="#22ff22">USAXS Ti shutter: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">USAXS Ti shutter: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='mono_shtr_opened']/value=1">
                                            <td bgcolor="#22ff22">mono: open</td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222">mono: closed</td>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='white_shtr_opened']/value=1">
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
                                                <a href="https://www3.aps.anl.gov/aod/blops/status/srStatus.html">
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
                                    <!-- TODO need to update this for 9-ID mirror system -->
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
                                        <xsl:otherwise>(mirror settings not available)</xsl:otherwise>
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
                            <font size="4">
                                <xsl:value-of select="//pv[@id='state']/value"/>
                            </font>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table border="1" width="100%" bgcolor="mintcream" rules="all">
                                <td align="left">spec macro:
                                    <a href="usaxs.mac">
                                        <xsl:attribute name="href">
                                        	<xsl:value-of select="//pv[@id='spec_macro_file']/value"/>
                                        </xsl:attribute>
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

		    <xsl:if test="//pv[@id='linkam_status']/value!=0">	<!-- start Linkam CI94 NIST 1500 status-->
			<tr>
 			    <td>
 				<table border="1" width="100%" bgcolor="mintcream" rules="all">
 				    <td align="left">Linkam 1500 temp:
 					<xsl:value-of select="//pv[@id='linkam_temp1']/value"
 					/> C </td>
 				    <td align="center">
 					<xsl:choose>
					    <xsl:when test="//pv[@id='linkam_status']/value=0"> stopped </xsl:when>
 					    <xsl:when test="//pv[@id='linkam_status']/value=1"> heating </xsl:when>
 					    <xsl:when test="//pv[@id='linkam_status']/value=2"> cooling </xsl:when>
 					    <xsl:when test="//pv[@id='linkam_status']/value=3"> limit end ramp </xsl:when>
 					    <xsl:when test="//pv[@id='linkam_status']/value=4"> hold limit time </xsl:when>
 					    <xsl:when test="//pv[@id='linkam_status']/value=5"> holding current temp </xsl:when>
					    <xsl:otherwise>
						    unknown status: <xsl:value-of select="//pv[@id='linkam_status']/value"/>
					    </xsl:otherwise>
				       </xsl:choose>
 				    </td>
 				    <td align="center">
 				       Rate: <xsl:value-of select="//pv[@id='linkam_rate']/value"/> C/min
 				    </td>
				    <td align="center">
				       Target Temp: <xsl:value-of select="//pv[@id='linkam_limit']/value"/>C
				    </td>
				    <xsl:choose>
				       <xsl:when test="//pv[@id='linkam_errors']/value=65408">
					    <td align="center" bgcolor="#22ff22">
					    No heater errors </td>
				       </xsl:when>
				       <xsl:otherwise>
					    <td align="center" bgcolor="#ff2222">Error in heater: <xsl:value-of select="//pv[@id='linkam_errors']/value"/></td>
				       </xsl:otherwise>
				    </xsl:choose>
 				</table>
 			    </td>
 			</tr>
		    </xsl:if>	<!-- end Linkam CI94 status-->
         
         	<tr>   <!-- start Linkam T96 status-->
 			    <td>
 				<table border="1" width="100%" bgcolor="mintcream" rules="all">
 				    <td align="left">Linkam 350V/600/1500V T/P    :
 					<xsl:value-of select="//pv[@id='linkamT96_temp']/value"
 					/> C/ <xsl:value-of select="//pv[@id='linkamT96_Pressure']/value"/> mBar
 				    </td>
 				    <td align="center">
 					<xsl:choose>
					    <xsl:when test="//pv[@id='linkamT96_status']/value=0"> stopped </xsl:when>
 					    <xsl:when test="//pv[@id='linkamT96_status']/value=1"> heating/cooling/holding </xsl:when>
 					    <xsl:otherwise>
						    unknown status: <xsl:value-of select="//pv[@id='linkamT96_status']/value"/>
					    </xsl:otherwise>
				       </xsl:choose>
 				    </td>
 				    <td align="center">
 				       Rate: <xsl:value-of select="//pv[@id='linkamT96_rate']/value"/> C/min
 				    </td>
				    <td align="center">
				       Target Temp: <xsl:value-of select="//pv[@id='linkamT96_limit']/value"/>C
				    </td>
				    <xsl:choose>
				       <xsl:when test="//pv[@id='linkamT96_errors']/value=0">
					    <td align="center" bgcolor="#22ff22">
					    No controller errors </td>
				       </xsl:when>
				       <xsl:otherwise>
					    <td align="center" bgcolor="#ff2222">
					    Controller Error!!!  </td>
				       </xsl:otherwise>
				    </xsl:choose>
 				</table>
 			    </td>
 			</tr>    <!-- end Linkam T96 status-->      
         
                </table>

                <br/>
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
                        <td>HHL (r,l,t,b)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='hhl_slitr']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='hhl_slitl']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='hhl_slitt']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='hhl_slitb']/value"/></td>
                    </tr>
                    <tr>
                        <td>mirror (r,l,t,b)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mir_slitr']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mir_slitl']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mir_slitt']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mir_slitb']/value"/></td>
                    </tr>
                    <tr>
                        <td>guard (r,l,t,b)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='GuardOutB']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='GuardInB']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='GuardTop']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='GuardBot']/value"/></td>
                    </tr>
                    <tr>
                        <td>USAXS (h,v)(gap,center)</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslith']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslitv']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslith0']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='uslitv0']/value"/></td>

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
                            <a href="showplot.html"><img SRC="livedata.png" alt="plot of USAXS data" WIDTH="200"/></a>
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
		    <!--
                    <tr>
                        <td>mirror</td>
                        <td bgcolor="#dddddd">< !-/- nothing -/-></td>
                        <td bgcolor="#dddddd">< !-/- nothing -/-></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mirr_x']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='mirr_vs']/value"/></td>
                        <td bgcolor="#dddddd">< !-/- nothing -/-></td>
                        <td bgcolor="#dddddd">< !-/- nothing -/-></td>
                    </tr>
		    -->
                    <tr>
                        <td>tcam</td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='tcam']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                    <tr>
                        <td>Pilatus</td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='pin_x']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='pin_y']/value"/></td>
                        <td bgcolor="white"><xsl:value-of select="//pv[@id='pin_z']/value"/></td>
                        <td bgcolor="#dddddd"><!-- nothing --></td>
                    </tr>
                </table>

                <br/>

            </body>

        </html>

    </xsl:template>

</xsl:stylesheet>
