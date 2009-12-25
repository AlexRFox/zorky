<?php

require_once ("common.php");

pstart ();

$logfile = sprintf ("%s/tmp/log.data", $aux_dir);
$outf = fopen ($logfile, "a");

$ts = strftime ("%Y-%d-%m %H:%M:%S");
fprintf ($outf, "\n");
fprintf ($outf, "%s\n", $ts);

foreach ($_REQUEST as $key => $val) {
	fprintf ($outf, "%s = %s\n", $key, $val);
}
fclose ($outf);

ob_clean ();
echo ("ok");
exit ();

?>
