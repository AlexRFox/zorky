<?php

require_once ("common.php");

pstart ();

$body .= "<div class='menu'>\n";
$body .= "<ul>\n";
$body .= sprintf ("<li>%s</li>\n", mklink ("readlog", "readlog.php"));

$t = sprintf ("api.php?start_game=zork1&debug=1&wave_id=t%d", rand () % 1000);
$body .= sprintf ("<li>%s</li>\n", mklink ("start_zork1", $t));
$body .= sprintf ("<li>%s</li>\n",
		  mklink ("kill_dfrotz", "api.php?kill_dfrotz=1"));
$body .= sprintf ("<li>%s</li>\n",
		  mklink ("list_procs", "index.php?list_procs=1"));
$body .= sprintf ("<li>%s</li>\n",
		  mklink ("avail_games", "api.php?list_avail_games=1"));
$body .= "</ul>\n";
$body .= "<div style='clear:both'></div>\n";
$body .= "</div>\n";

$arg_list_procs = 0 + @$_REQUEST['list_procs'];
$arg_kill = trim (rawurldecode (@$_REQUEST['kill']));

$db = get_db ();

if ($arg_list_procs == 1) {
	exec ("ps ax | grep dfrotz", $ret);
	$body .= "<pre>\n";
	foreach ($ret as $str) {
		$body .= h($str) . "\n";
	}
	$body .= "</pre>\n";
	pfinish ();
}

if ($arg_kill) {
	$q = query_db ($db,
		       "select pid"
		       ." from zorky"
		       ." where wave_id = ?",
		       $arg_kill);
	if (($r = fetch ($q)) != NULL) {
		$pid = $r->pid;

		posix_kill ($pid, 15);
		query_db ($db, "delete from zorky where wave_id = ?",
			  $arg_kill);
		redirect ("index.php");
	}
}

$body .= "<h1>Current games</h1>\n";

$q = query_db ($db,
	       "select id, wave_id,"
	       ." to_char (dttm, 'YYYY-MM-DD HH24:MI:SS') as dttm,"
	       ." name, pid"
	       ." from zorky"
	       ." order by dttm");
$body .= "<table class='games_list'>\n";
$body .= "<tr class='games_heading'>"
	."<th>Id</th>"
	."<th>Start</th>"
	."<th>Game</th>"
	."<th>Wave</th>"
	."<th>PID</th>"
	."<th>Op</th>"
	."</tr>\n";
while (($r = fetch ($q)) != NULL) {
	$id = 0 + $r->id;
	$wave_id = $r->wave_id;
	$dttm = $r->dttm;
	$name = $r->name;
	$pid = $r->pid;

	$kill_target = sprintf ("index.php?kill=%s", rawurlencode ($wave_id));
	$data_target = sprintf ("api.php?wave_id=%s&get_data=1&debug=1",
				rawurlencode ($wave_id));

	$body .= "<tr>\n";
	$body .= sprintf ("<td>%s</td>", mklink($id, $data_target));
	$body .= sprintf ("<td>%s</td>", mklink($dttm, $data_target));
	$body .= sprintf ("<td>%s</td>", mklink($name, $data_target));
	$body .= sprintf ("<td>%s</td>", mklink($wave_id, $data_target));
	$body .= sprintf ("<td>%s</td>", mklink($pid, $data_target));
	$body .= "<td>";
	$body .= mklink ("kill", $kill_target);
	$body .= "</td>";
	$body .= "</tr>\n";
}
$body .= "</table>\n";



pfinish ();

?>
