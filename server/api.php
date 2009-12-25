<?php

require_once ("common.php");

$start_game = trim (@$_REQUEST['start_game']);

if ($start_game) {
	if (ereg ('[^-_a-zA-Z0-9]', $start)) {
		echo ("invalid game");
		exit ();
	}
	
	$cmd = sprintf ("%s/bin/run-dfrotz -L -k %s %s",
			$aux_dir, $conf_key, $start_game);
	exec ($cmd, $result);

	var_dump ($result);

	exit ();
}


$cmd = @$_REQUEST['cmd'];

$ret = (object)NULL;
$ret->status = "ok";
$ret->echo = $cmd;

ob_clean ();
echo (json_encode ($ret));
exit ();

?>
