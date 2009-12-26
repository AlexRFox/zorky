#! /usr/bin/env python

import httplib, simplejson, urllib, urllib2

production = "http://zorky.willisson.org/"
development = "http://rhino.local:9001/"

if True:
    hosturl = production
else:
    hosturl = development

def send_cmd (wave_id, cmd = "l"):
    params = urllib.urlencode ({"get_data": 1, "wave_id": wave_id, "cmd": cmd})

    r1 = urllib2.urlopen (hosturl + "api.php?" + params)

    decjson = simplejson.load (r1)

    return decjson

def start (wave_id, game_name = "zork1"):
    params = urllib.urlencode ({"start_game": game_name, "wave_id": wave_id})
    
    r1 = urllib2.urlopen (hosturl + "api.php?" + params)

    decjson = simplejson.load (r1)
    
    return decjson

def game_list ():
    params = urllib.urlencode ({"list_avail_games": 1})

    r1 = urllib2.urlopen (hosturl + "api.php?" + params)
    
    decjson = simplejson.load (r1)

    return decjson
