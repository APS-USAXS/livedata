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
                <title>USAXS: EPICS process variables</title>
            </head>
            <body>
                <h1>USAXS: EPICS process variables</h1>
                <p>written by: <xsl:value-of select="/usaxs_pvs/writer"/></p>
                <p>date/time stamp: <xsl:value-of select="/usaxs_pvs/datetime"/></p>
                
                <table border="2">
                    <tr>
                        <th>name</th>
                        <th>id</th>
                        <th>description</th>
                        <th>value</th>
                        <th>units</th>
                        <th>timestamp</th>
                    </tr>
                    <xsl:apply-templates select="usaxs_pvs/pv"/>
                </table>

                <hr />
		<p>
                    <small>
                        report page: $Id$
                    </small>
                </p>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="pv">
        <tr>
 	    <xsl:if test="position() mod 2=0">
 	      <xsl:attribute name="bgcolor">Azure</xsl:attribute>
 	    </xsl:if>
            <td><xsl:value-of select="name"/></td>
            <td><xsl:value-of select="id"/></td>
            <td><xsl:value-of select="description"/></td>
            <td><xsl:value-of select="value"/></td>
            <td><xsl:value-of select="units"/></td>
            <td><xsl:value-of select="timestamp"/></td>
        </tr>
    </xsl:template>

</xsl:stylesheet>
