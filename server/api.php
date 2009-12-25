<?php

require_once ("common.php");

$arg_debug = 0 + @$_REQUEST['debug'];

$arg_start_game = trim (@$_REQUEST['start_game']);
$arg_kill_dfrotz = 0 + @$_REQUEST['kill_dfrotz'];
$arg_game_id = 0 + @$_REQUEST['game_id'];
$arg_get_data = 0 + @$_REQUEST['get_data'];
$arg_cmd = trim (@$_REQUEST['cmd']);
$arg_list_avail_games = 0 + @$_REQUEST['list_avail_games'];

if ($arg_list_avail_games == 1) {
	$names = array ();

	$dir = opendir ($aux_dir . "/z5");
	while (($name = readdir ($dir)) != NULL)
		$names[] = $name;

	$ret = (object)NULL;
	$ret->names = $names;
	echo (json_encode ($ret));
	exit ();
}

if ($arg_kill_dfrotz == 1) {
	exec ("killall run-dfrotz");
	redirect ("index.php");
}

if ($arg_start_game) {
	if (ereg ('[^-_a-zA-Z0-9]', $start)) {
		echo ("invalid game");
		exit ();
	}
	
	$cmd = sprintf ("%s/bin/run-dfrotz -L -k %s %s",
			$aux_dir, $conf_key, $arg_start_game);
	exec ($cmd, $result);

	$game_id = 0 + $result[0];

	$ret = (object)NULL;
	$ret->game_id = $game_id;

	$jret = json_encode ($ret);

	if ($arg_debug == 1) {
		pstart ();
		$body .= "<pre>\n";
		$body .= h($jret);
		$body .= "</pre>\n";

		$t = sprintf ("api.php?game_id=%d&get_data=1&debug=1",
			      $game_id);
		$body .= mklink ("getdata", $t);
		pfinish ();
	}

	ob_clean ();
	echo (json_encode ($ret));
	exit ();
}


if ($arg_get_data == 1) {
	$port = $arg_game_id;

	$sock = socket_create (AF_INET, SOCK_STREAM, 0);
	socket_connect ($sock, "localhost", $port);
	if ($arg_cmd)
		socket_write ($sock, $arg_cmd."\n");
	$val = socket_read ($sock, 100000);
	socket_close ($sock);

	$ret = (object)NULL;
	$ret->dispay = $val;

	$jret = json_encode ($ret);

	if ($arg_debug) {
		pstart ();
		$body .= "<pre>\n";
		$body .= h(wordwrap ($jret));
		$body .= "</pre>\n";

		$body .= "<form action='api.php'>\n";
		$body .= sprintf ("<input type='hidden'"
				  ." name='game_id' value='%d' />\n",
				  $arg_game_id);
		$body .= "<input type='hidden' name='debug' value='1' />\n";
		$body .= "<input type='hidden' name='get_data' value='1' />\n";
		$body .= "<input type='text' name='cmd' />\n";
		$body .= "<input type='submit' value='submit' />\n";
		$body .= "</form>\n";

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
