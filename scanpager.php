<?php
 //  http://usaxs.xray.aps.anl.gov/livedata/scanpager.php?pageID=99999
 //
 //  http://www.w3schools.com/php/php_ref_simplexml.asp
 //  http://pear.php.net/package/Pager
 //  http://www.plus2net.com/php_tutorial/php_paging.php
 //  http://devzone.zend.com/1038/paging-data-sets-with-pear-pager/
 
 // NOTE:  The pear Pager may not be the *best* choice here.
 //  With each page load, we parse the entire XML file.
 //  While reading only what we want to view  would be a major optimization,
 //  _any_ pager is better than loading the entire XML file
 //  through an XSLT when most folks just want to see the most 
 //  recent scan information.
?>

<html>
  <head />
  <body>

    <h1>USAXS instrument: scan log</h1>

    <?php

    // TODO: allow user to sort by column (alternate between up or down sorts)
    // TODO: allow user to select number per page
    // TODO: allow user to pick any page
    // TODO: allow user to search

    // include class
    include_once 'Pager/Pager.php';

    $xmlFile = "scanlog.xml";
    $xml=simplexml_load_file($xmlFile) or die("Error: Cannot create object");
    $data = json_decode(json_encode($xml),TRUE);

    // set pager options
    $params = array(
  	'mode'     => 'Sliding',
  	'perPage'  => 20,
  	'delta'    => 3,
  	'itemData' => $data["scan"],
 	'spacesBeforeSeparator' => 2,
 	'spacesAfterSeparator'  => 2,
	'firstPageText' => 'oldest',
	'lastPageText' => 'current',
  	//'currentPage'  => 20000,
    );
    
    function item_datetime_str($item) {
      //print_r($item);
      $str = $item["@attributes"]["date"];
      $str .= ' ';
      $str .= $item["@attributes"]["time"];
      return $str;
    }

    // generate pager object
    $pager =& Pager::factory($params);

    // get links for current page and print
    $links = $pager->getLinks();
    echo $links['all'];

    ?>
    
    <table border="2" width="100%">
      <tr style="background-color: grey; color: white;">
        <th>index</th>
        <th>title</th>
        <th>type</th>
        <th>scan</th>
        <th>file</th>
        <th>started</th>
        <th>ended</th>
      </tr>
    <?php

    // get data for current page and make a table
    $count = ($pager->getCurrentPageID()-1) * $params["perPage"];
    foreach ($pager->getPageData() as $item) {
	//print_r($item);
	$count += 1;
	if ($count % 2)
	  echo "      <tr>\n";
	else
	  echo "      <tr bgcolor=\"Azure\">\n";
  	echo "        <td>" . $count . "</td>\n";
  	echo "        <td>" . $item["title"] . "</td>\n";
	// TODO: make an href to the SPEC plot
  	echo "        <td>" . $item["@attributes"]["type"] . "</td>\n";
  	echo "        <td>" . $item["@attributes"]["number"] . "</td>\n";
  	echo "        <td>" . $item["file"] . "</td>\n";
  	echo "        <td>" . item_datetime_str($item["started"]) . "</td>\n";
	if ("complete" == $item["@attributes"]["state"])
  	    echo "        <td>" . item_datetime_str($item["ended"]) . "</td>\n";
	else
  	    echo "        <td>" . $item["@attributes"]["state"] . "</td>\n";
	echo "      </tr>\n";
    }
    ?>
    </table>
    
    <?php

    // get links for current page and print
    $links = $pager->getLinks();
    echo $links['all'];
    
    ?>

  </body>
</html>

<!--
########### SVN repository information ###################
# $Date$
# $Author$
# $Revision$
# $URL$
# $Id$
########### SVN repository information ###################
-->
