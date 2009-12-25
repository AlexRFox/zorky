#! /usr/bin/env python

import httplib, urllib, simplejson

hosturl = "willisson.org"
port = 9001

def sendcmd (cmd, game_id = 38978):
    safecmd = urllib.quote (cmd)
    tar = "/api.php?get_data=1&game_id=" + str (game_id) + "&cmd=" + safecmd
    conn = httplib.HTTPConnection (hosturl, port)
    conn.request ("GET", tar)
    r1 = conn.getresponse ()

    decjson = simplejson.load (r1)

    return decjson

def start (game_name = "zork1"):
    conn = httplib.HTTPConnection (hosturl, port)
    conn.request ("GET", "/api.php?startgame=zork1")
    r1 = conn.getresponse ()

    decjson = simplejson.load (r1)
    
    return decjson
