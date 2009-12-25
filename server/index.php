<?php

require_once ("common.php");

pstart ();

$body .= "<div>\n";
$body .= mklink ("api", "api.php");
$body .= " | ";
$body .= mklink ("readlog", "readlog.php");
$body .= " | ";
$body .= mklink ("start_zork1", "api.php?start_game=zork1&debug=1");
$body .= " | ";
$body .= mklink ("kill_dfrotz", "api.php?kill_dfrotz=1");
$body .= " | ";
$body .= mklink ("list_procs", "index.php?list_procs=1");
$body .= " | ";
$body .= mklink ("list_avail_games", "api.php?list_avail_games=1");
$body .= "</div>\n";

$body .= "<form action='api.php'>\n";
$body .= "<input type='text' name='cmd' />\n";
$body .= "<input type='submit' value='Send' />\n";
$body .= "</form>\n";

$arg_list_procs = 0 + @$_REQUEST['list_procs'];

if ($arg_list_procs == 1) {
	exec ("ps ax | grep dfrotz", $ret);
	$body .= "<pre>\n";
	foreach ($ret as $str) {
		$body .= h($str) . "\n";
	}
	$body .= "</pre>\n";
	pfinish ();
}


pfinish ();

?>
