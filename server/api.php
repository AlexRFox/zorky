<?php

require_once ("common.php");

$db = get_db ();

$arg_debug = 0 + @$_REQUEST['debug'];

$arg_start_game = trim (@$_REQUEST['start_game']);
$arg_end_game = trim (@$_REQUEST['end_game']);
$arg_kill_dfrotz = 0 + @$_REQUEST['kill_dfrotz'];
$arg_get_data = 0 + @$_REQUEST['get_data'];
$arg_cmd = trim (@$_REQUEST['cmd']);
$arg_list_avail_games = 0 + @$_REQUEST['list_avail_games'];
$arg_list_saved_games = trim (rawurldecode (@$_REQUEST['list_saved_games']));
$arg_check_wave_id = trim (rawurldecode (@$_REQUEST['check_wave_id']));
$arg_wave_id = trim (rawurldecode (@$_REQUEST['wave_id']));

if ($arg_list_saved_games) {
	$ret = (object)NULL;

	$q = query_db ($db, "select id from zorky where wave_id = ?",
		       $arg_wave_id);
		
	if (($r = fetch ($q)) == NULL) {
		$ret->error = "wave_id not found";
		echo (json_encode ($ret));
		exit ();
	}
		
	$id = 0 + $r->id;
	$game_dir = opendir (sprintf ("%s/tmp/game-%d", $aux_dir, $id));
	$names = array ();

	while (($name = readdir ($game_dir)) != NULL) {
		if (ereg ('\.z5$', $name) == 0
		    && $name != "dfrotz"
		    && $name != '.'
		    && $name != '..') {
			$names[] = $name;
		}
	}
		
	if (count ($names) == 0) {
		$ret->error = "no saved games";
		echo (json_encode ($ret));
		exit ();
	}

	$ret->names = $names;
	echo (json_encode ($ret));
	exit ();
}

if ($arg_list_avail_games == 1) {
	$names = array ();

	$dir = opendir ($aux_dir . "/z5");
	while (($name = readdir ($dir)) != NULL) {
		if (ereg ('\.z5$', $name))
			$names[] = $name;
	}

	$ret = (object)NULL;
	$ret->names = $names;
	echo (json_encode ($ret));
	exit ();
}

if ($arg_kill_dfrotz == 1) {
	exec ("killall run-dfrotz");
	redirect ("index.php");
}

if ($arg_check_wave_id) {
	$ret = (object)NULL;

	$q = query_db ($db, "select 0 from zorky where wave_id = ?",
		       $arg_check_wave_id);

#	if (($r = fetch ($q)) == NULL) {
	if (0) {
		$ret->status = 1;
		echo (json_encode ($ret));
		exit ();
	} else {
		$ret->status = 0;
		echo (json_encode ($ret));
		exit ();
	}
}	

function get_data ($port) {
	global $arg_cmd;

	$sock = socket_create (AF_INET, SOCK_STREAM, 0);
	socket_connect ($sock, "localhost", $port);
	if ($arg_cmd)
		socket_write ($sock, $arg_cmd."\n");
	$val = socket_read ($sock, 100000);
	socket_close ($sock);
	return ($val);
}


if ($arg_start_game) {
	if (ereg ('[^-_a-zA-Z0-9]', $start)) {
		echo ("invalid game");
		exit ();
	}
	
	$q = query_db ($db, "select nextval('seq') as seq");
	$r = fetch ($q);
	$id = 0 + $r->seq;

	$game_dir = sprintf ("%s/tmp/game-%d", $aux_dir, $id);

	$cmd = sprintf ("%s/bin/run-dfrotz -L -k %s -d %s %s",
			$aux_dir, $conf_key, $game_dir, $arg_start_game);
	exec ($cmd, $result);

	sscanf ($result[0], "%d %d", $port, $pid);

	if ($arg_wave_id && $port) {
		query_db ($db,
			  "insert into zorky (id, wave_id, port, name, pid)"
			  ." values (?,?,?,?,?)",
			  array ($id, $arg_wave_id, $port,
				 $arg_start_game, $pid));

		query_db ($db, "commit work");
	}


	sleep (1);
	

	$ret = (object)NULL;
	$ret->status = "ok";
	$ret->display = get_data ($port);

	$jret = json_encode ($ret);

	if ($arg_debug == 1) {
		redirect ("index.php");
	}

	ob_clean ();
	echo (json_encode ($ret));
	exit ();
}

if ($arg_end_game) {
	$ret = (object)NULL;

	$q = query_db ($db,
		       "select pid from zorky where wave_id = ?",
		       $arg_end_game);

	if (($r = fetch ($q)) != NULL) {
		$pid = 0 + $r->pid;

		posix_kill ($pid, 15);

		query_db ($db, "delete from zorky where wave_id = ?",
			  $arg_end_game);
		do_commits ();

		$ret->display = "game ended";
		echo (json_encode ($ret));
		exit ();
	} else {
		$ret->error = "wave_id not found";
		echo (json_encode ($ret));
		exit ();
	}
}

if ($arg_get_data == 1) {
	$q = query_db ($db,
		       "select port"
		       ." from zorky"
		       ." where wave_id = ?",
		       $arg_wave_id);
	if (($r = fetch ($q)) == NULL) {
		$ret = (object)NULL;
		$ret->error = "wave_id not found";
		echo (json_encode ($ret));
		exit ();
	}

	$port = $r->port;

	$val = get_data ($port);

	$ret = (object)NULL;
	$ret->display = $val;

	$jret = json_encode ($ret);

	if ($arg_debug) {
		pstart ();
		$body .= "<pre>\n";
		$body .= h(wordwrap ($jret));
		$body .= "</pre>\n";

		$body .= "<form action='api.php'>\n";
		$body .= sprintf ("<input type='hidden'"
				  ." name='wave_id' value='%s' />\n",
				  h($arg_wave_id));
		$body .= "<input type='hidden' name='debug' value='1' />\n";
		$body .= "<input type='hidden' name='get_data' value='1' />\n";
		$body .= "<input type='text' name='cmd' />\n";
		$body .= "<input type='submit' value='submit' />\n";
		$body .= "</form>\n";

		$body .= mklink ("[back to home]", "index.php");
		$t = sprintf ("api.php?wave_id=%s&list_saved_games=1",
			      h($arg_wave_id));
		$body .= mklink ("[list saved games]", $t);
		pfinish ();
	}

	ob_clean ();
	echo ($jret);
	exit ();
}
		


$ret = (object)NULL;
$ret->status = "ok";
$ret->echo = $arg_cmd;

ob_clean ();
echo (json_encode ($ret));
exit ();

?>
