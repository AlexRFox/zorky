#! /usr/bin/env python

import httplib, urllib, simplejson

hosturl = "willisson.org"
port = 9001

def sendcmd (cmd, game_id = 0):
    if gameid == 0:
        game_id = 38978
    safecmd = urllib.quote (cmd)
    tar = "/api.php?get_data=1&game_id=" + str (game_id) + "&cmd=" + safecmd
    conn = httplib.HTTPConnection (hosturl, port)
    conn.request ("GET", tar)
    r1 = conn.getresponse ()
    encjson = r1.read ()

    decjson = simplejson.loads (encjson)

    return decjson

#def start ():
#    conn = httplib.HTTPConnection (hosturl, port)
#    conn.request ("GET", tar



#http://willisson.org:9001/api.php?start_game=zork1&debug=1
