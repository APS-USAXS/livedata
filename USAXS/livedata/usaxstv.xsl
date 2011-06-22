<?xml version="1.0" encoding="UTF-8"?>

<!-- 
    $Id$
    $URL$
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<xsl:template match="/">

<html>
<head>
<meta http-equiv="Pragma" content="no-cache"/>
 <xsl:choose>
                                        <xsl:when test="contains(//pv[@id='state']/value,'Radiography Mode')">
					<meta http-equiv="Refresh" content="60" />
                                        </xsl:when>
                                        <xsl:otherwise>
                                        <meta http-equiv="Refresh" content="10" />
					</xsl:otherwise>
                                    </xsl:choose>

<meta http-equiv="Refresh" content="60"/>
<title>USAXS: TV status</title>
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
<table border="0" width="100%" bgcolor="mintcream" rules="all"><tr>
<td width="56%">
 <xsl:choose>
                                        <xsl:when test="contains(//pv[@id='state']/value,'Radiography Mode')">
					    <script language="javascript">
					    
						if (navigator.userAgent.match(/like Mac OS X/i)) {
                document.write('<img src="http://usaxsaxis1.cars.aps.anl.gov/axis-cgi/jpg/image.cgi?resolution=vga&amp;amp;camera=4" width="100%" />');
                }
	else {
		document.write('<img src="http://usaxsaxis1.cars.aps.anl.gov/axis-cgi/mjpg/video.cgi?resolution=VGA&amp;amp;camera=4" width="100%" />');
        }
        
                                        </script>
					</xsl:when>
                                        <xsl:otherwise>
											<img src="http://usaxs.xor.aps.anl.gov/livedata/livedata.png" width="100%" />
                                        </xsl:otherwise>
                                    </xsl:choose>

</td>

<td width="44%">
<table width="100%" bgcolor="mintcream" rules="all"><tr>
<td bgcolor="darkblue" align="center">
<font color="white" size="6">
<xsl:comment>
   FIXME: Fonts of links look too dark!  Need to adjust by setting proper style attributes!
</xsl:comment>
<a href="http://usaxs.xor.aps.anl.gov/livedata/"> _ </a>

USAXS 

status

<xsl:comment>FIXME: again, too dark</xsl:comment><a href="http://usaxs.xor.aps.anl.gov/livedata/raw-report.html"> _ </a>
</font></td></tr>

<tr><td bgcolor="darkblue" align="center">
<font color="white" size="4">updated  <xsl:value-of select="/usaxs_pvs/datetime"/></font></td></tr>
<tr><td height="75px"><br /></td></tr>

<tr>                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='D_beam_ready']/value=1">
                                            <td bgcolor="#22ff22" align="center"><font size="3">
                                              PSS: D Beam Ready </font></td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222" align="center"><font size="3">
                                                PSS: D Beam Not Ready</font></td>
                                        </xsl:otherwise>
                                    </xsl:choose>
</tr>

<tr>                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='D_beam_active']/value=1">
                                            <td bgcolor="#22ff22" align="center"><font size="3">
                                             
                                               PSS: D Beam Active</font></td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222" align="center"><font size="3">
                                                PSS: D Beam Inactive</font></td>
                                                
                                        </xsl:otherwise>
                                    </xsl:choose>
</tr>


<tr>                                    <xsl:choose>
                                        <xsl:when test="//pv[@id='SR_current']/value>2">
                                            <td bgcolor="#22ff22" align="center"><font size="3">
                                             
                                                APS current =
                                                <xsl:value-of select="//pv[@id='SR_current']/value"/> mA</font></td>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <td bgcolor="#ff2222" align="center"><font size="3">
                                                    APS current =
                                                <xsl:value-of select="//pv[@id='SR_current']/value"/> mA</font></td>
                                        </xsl:otherwise>
                                    </xsl:choose>
</tr>

<tr><td align="center"><font size="3">I0: <xsl:value-of select="//pv[@id='I0_VDC']/value"/> V</font></td></tr>

                       <tr>         <xsl:choose>
                                    <xsl:when test="//pv[@id='USAXS_collecting']/value=1">
                                        <td bgcolor="#22ff22" align="center"><font size="3">USAXS scan running</font></td>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <td align="center"><font size="3">not scanning USAXS</font></td>
                                    </xsl:otherwise>
                                </xsl:choose>

<tr><td height="75px"><br /></td></tr>
<tr><td align="center" bgcolor="bisque"><font size="5">
                            <xsl:value-of select="//pv[@id='sampleTitle']/value"/>

    </font></td></tr>
<tr><td align="center" bgcolor="lightblue"><font size="5">
                                <xsl:value-of select="//pv[@id='state']/value"/>

    </font></td></tr>
<tr><td height="75px"><br /></td></tr>
<tr><td align="center"><font size="3">
                                    <xsl:value-of select="//pv[@id='spec_dir']/value"
                                    />/<xsl:value-of select="//pv[@id='spec_data_file']/value"
                                    />

    </font></td></tr>
<tr><td align="center"><font size="3">
                                    scan #<xsl:value-of select="//pv[@id='spec_scan']/value"/>

   </font> </td></tr>
<tr><td align="center"><font size="3">
                                    <xsl:value-of select="//pv[@id='spec_scan']/timestamp"/>

    </font></td></tr></tr>
</table>
</td></tr></table>
</body>
</html>
    </xsl:template>

</xsl:stylesheet>
