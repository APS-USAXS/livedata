<?xml version='1.0' encoding='UTF-8'?>
<!--
########### SVN repository information ###################
# $Date: 2009-02-22 15:30:17 -0600 (Sun, 22 Feb 2009) $
# $Author: jemian $
# $Revision: 2040 $
# $HeadURL: https://subversion.xor.aps.anl.gov/bcdaioc/15iddUSX/15iddUSXApp/op/s15usaxs/scanLog/scanlog.xsl $
# $Id: scanlog.xsl 2040 2009-02-22 21:30:17Z jemian $
########### SVN repository information ###################
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" omit-xml-declaration="yes" indent="yes" />

  <xsl:template match="/">
    <html>
      <body>
 	<h1>USAXS scan log</h1>
 	<table border="2">
 	  <tr style="background-color: grey; color: white;">
 	    <th>index</th>
 	    <th>title</th>
 	    <th>type</th>
 	    <th>scan</th>
 	    <th>file</th>
 	    <th>started</th>
 	    <th>ended</th>
 	  </tr>
 	  <xsl:apply-templates select="//scan">
 	    <xsl:sort select="position()" order="descending" data-type="number"/>
 	  </xsl:apply-templates>
 	</table>
 	<hr />
 	<small><center>generated from scanlog.xml by XSLT translation</center></small>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="scan">
    <tr>
      <xsl:if test="position() mod 2=0">
        <xsl:attribute name="bgcolor">Azure</xsl:attribute>
      </xsl:if>
      <td><xsl:value-of select="last()-position()+1" /></td>
      <td><xsl:value-of select="title" /></td>
      <td><xsl:value-of select="@type" /></td>
      <td><xsl:value-of select="@number" /></td>
      <td><xsl:value-of select="file" /></td>
      <td>
        <xsl:value-of select="started/@date" /> 
        <xsl:text> </xsl:text>
        <xsl:value-of select="started/@time" />
      </td>
      <xsl:choose>
        <xsl:when test="@state='scanning'">
	  <td>scanning</td>
        </xsl:when>
	<xsl:otherwise>
	  <td>
        <xsl:value-of select="ended/@date" /> 
        <xsl:text> </xsl:text>
        <xsl:value-of select="ended/@time" />
      </td>
	</xsl:otherwise>
      </xsl:choose>
    </tr>
  </xsl:template>

</xsl:stylesheet>

