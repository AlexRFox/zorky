<?php

require_once ("common.php");

pstart ();

$body .= mklink ("api", "api.php");

$body .= "<form action='api.php'>\n";
$body .= "<input type='text' name='cmd' />\n";
$body .= "<input type='submit' value='Send' />\n";
$body .= "</form>\n";

pfinish ();

?>
