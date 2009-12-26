#! /usr/bin/env python

import httplib, urllib, simplejson

production = "willisson.org"
development = "rhino.local"

if False:
    hosturl = production
else:
    hosturl = development

port = 9001

def sendcmd (wave_id, cmd):
    safecmd = urllib.quote (cmd)
    tar = "/api.php?get_data=1&wave_id=" + str (wave_id) + "&cmd=" + safecmd
    conn = httplib.HTTPConnection (hosturl, port)
    conn.request ("GET", tar)
    r1 = conn.getresponse ()

    decjson = simplejson.load (r1)

    return decjson

def start (wave_id, game_name = "zork1"):
    conn = httplib.HTTPConnection (hosturl, port)
    tar = "/api.php?start_game=" + game_name + "&wave_id=" + wave_id
    conn.request ("GET", tar)
    r1 = conn.getresponse ()

    decjson = simplejson.load (r1)
    
    return decjson

def game_list ():
    conn = httplib.HTTPConnection (hosturl, port)
    conn.request ("GET", "/api.php?list_avail_games=1")
    r1 = conn.getresponse ()

    decjson = simplejson.load (r1)

    return decjson
