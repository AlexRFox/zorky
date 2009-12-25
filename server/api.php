<?php

require_once ("common.php");

$cmd = @$_REQUEST['cmd'];

$ret = (object)NULL;
$ret->status = "ok";
$ret->echo = $cmd;

ob_clean ();
echo (json_encode ($ret));
exit ();

?>
