<?php

require_once ("common.php");

pstart ();

$arg_clearlog = 0 + @$_REQUEST['clearlog'];

$logfile = sprintf ("%s/tmp/log.data", $aux_dir);


if ($arg_clearlog == 1) {
	fopen ($logfile, "w");
	redirect ("readlog.php");
}

$body .= "<form action='readlog.php'>\n";
$body .= "<input type='hidden' name='clearlog' value='1' />\n";
$body .= "<input type='submit' value='clear log' />\n";
$body .= "</form>\n";

$body .= "<pre>\n";
$body .= h(@file_get_contents ($logfile));
$body .= "</pre>\n";

pfinish ();

?>
