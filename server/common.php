<?php

$dbg_file = NULL;

function set_dbg_file ($basename) {
	global $dbg_file, $aux_dir;
	if ($dbg_file) {
		fclose ($dbg_file);
		$dbg_file = NULL;
	}
	
	$fullname = strftime ("$aux_dir/log/$basename.%m%d");
	$dbg_file = fopen ($fullname, "a");
}

function dbg ($str) {
	global $dbg_file, $db_mode, $last_t;
	global $aux_dir, $login_id;
	if ($dbg_file == NULL) {
		$filename = strftime ("$aux_dir/log/peb-$db_mode.%m%d");
		if (($dbg_file = fopen ($filename, "a")) == NULL)
			return;
	}

	if ($str == NULL) {
		fputs ($dbg_file, "\n");
	} else{
		$arr = gettimeofday ();

		$secs = $arr['sec'];
		$millisecs = floor ($arr['usec'] / 1000);

		fputs ($dbg_file,
		       sprintf ("%s.%03d %s %d %s\n",
				strftime ("%H:%M:%S", $secs),
				$millisecs,
				$_SERVER['REMOTE_ADDR'],
				$login_id,
				trim ($str)));
	}
	fflush ($dbg_file);
}

global $db_mode;
$db_mode = trim (@$_SERVER['db_mode']);

if ($db_mode != "dev" && $db_mode != "test" && $db_mode != "production") {
	echo ("missing SetEnv db_mode in httpd conf");
	var_dump ($_SERVER);
	exit ();
}

require_once (sprintf ("%s/zorky-conf.php", $_SERVER['DOCUMENT_ROOT']));

global $aux_dir, $site_dir, $mt_cgi_dir, $conf_key;

function h($val) {
	return (htmlentities ($val, ENT_QUOTES, 'UTF-8'));
}

function fix_target ($path) {
	$path = ereg_replace ("&", "&amp;", $path);
	return ($path);
}

function mklink ($text, $target) {
	if (trim ($text) == "")
		return ("");
	if (trim ($target) == "")
		return (h($text));
	return (sprintf ("<a href='%s'>%s</a>",
			 fix_target ($target), h($text)));
}

function ckerr ($str, $obj, $aux = "")
{
	global $db_mode;

	if (DB::isError ($obj)) {
		$ret = "";

		$ret = sprintf ("<p>DBERR %s: %s<br />\n",
				h($str),
				h($obj->getMessage ()),
				"");

		if ($db_mode == "dev") {
			/* these fields might have db connect passwords */
			$ret .= "<strong style='background:#fee'>"
				." extra info for dev:";
			$ret .= h($obj->userinfo);
			if ($aux != "")
				$ret .= sprintf ("<p>aux info: %s</p>\n",
						 h($aux));
			$ret .= "</strong>\n";
		}
		$ret .= "</p>";

		echo ($ret);
		exit ();
	}
}

global $raw_dbs;

function get_raw_db ($dbname)
{
	global $raw_dbs;

	if (! isset ($raw_dbs)) {
		require 'DB.php';
		$raw_dbs = array ();
	}

	if (isset ($raw_dbs[$dbname]))
		return ($raw_dbs[$dbname]);
	
	$dbinfo = sprintf ("pgsql://apache@/%s", $dbname);
	$d = new DB;
	$db = $d->connect ($dbinfo);
	ckerr ("connect/local", $db);
	
	$raw_dbs[$dbname] = $db;

	return ($db);
}

function query_db ($dp, $stmt, $arr = NULL) {
	$q = $dp->query ($stmt, $arr);
	ckerr ($stmt, $q);
	return ($q);
}

function fetch ($q) {
	return ($q->fetchRow (DB_FETCHMODE_OBJECT));
}

function make_absolute ($rel) {
	if (ereg ("^http", $rel) == 0) {
		if (ereg ("^/", $rel)) {
			if (@$_SERVER['HTTPS'] == "on") {
				$abs = "https://";
			} else {
				$abs = "http://";
			}
			$abs .= $_SERVER['HTTP_HOST']; /* may include port */
			$abs .= $rel; /* rel already starts with slash */
		} else {
			$abs = $_SERVER['SCRIPT_URI'];
			$abs = ereg_replace ('[^/]*$', "", $abs);
			if (ereg ('/$', $abs) == 0)
				$abs .= "/";
			$abs .= $rel;
		}
	} else {
		$abs = $rel;
	}
	return ($abs);
}

function redirect ($target) {
	$target = make_absolute ($target);

	if ($debug || $stop_redirect) {
		global $login_id, $anon_ok;
		echo ("debug or stop redirect... $login_id $anon_ok ");
		var_dump ($target);
		var_dump ($_SERVER);

		$s = trim (@$_SESSION['flash']);

		if ($s != "") {
			$body .= "<p>pending flash: \n";
			$body .= h($s);
			$body .= "</p>\n";
		}

		$body .= "<p>";
		$body .= mklink ("(dbg=1: click here to finish redirect)",
				 $target);
		$body .= "</p>\n";
		foobar ();
		pfinish ();
	}

	session_write_close ();

	ob_clean ();
	header ("Location: $target");
	exit ();
}


function pstart () {
	ob_start ();
	global $body;
	$body = "";
}

function pstart_nocache () {
	pstart ();
	header ("Cache-Control: no-store, no-cache, must-revalidate,"
		." post-check=0, pre-check=0");
	header ("Pragma: no-cache");
	header ("Expires: Thu, 19 Nov 1981 08:52:00 GMT");
}

function pfinish () {
	global $body;

	$ajax = 0;

	if (isset ($_SERVER['HTTP_X_REQUESTED_WITH']))
		$ajax = 1;

	if ($ajax) {
		echo ($body);
		exit ();
	}

	$ret = "";

	$ret .= "<!DOCTYPE html PUBLIC"
		." '-//W3C//DTD XHTML 1.0 Transitional//EN'"
		." 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>"
		."\n";
	$ret .= "<html xmlns='http://www.w3.org/1999/xhtml'"
		." id='sixapart-standard'>\n";
	$ret .= "<head>\n";

	$ret .= "<meta http-equiv='Content-Type'"
		." content='text/html; charset=utf-8' />\n"
		."<script type='text/javascript' src='/mt.js'></script>\n"
		."<link rel='stylesheet' type='text/css'"
		." href='/zorky.css' media='screen' />\n";


	$ret .= "<title>Zorky</title>\n";
	$ret .= "</head>\n";

	$ret .= "<body>\n";

	echo ($ret);

	global $body;
	echo ($body);

	$ret = "";
	$ret .= "</body>\n"
		."</html>\n";

	echo ($ret);

	exit ();
}



?>
