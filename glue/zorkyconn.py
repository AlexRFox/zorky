#! /usr/bin/env python

import httplib, simplejson, urllib2

production = "http://willisson.org:9001/"
development = "http://rhino.local:9001/"

if True:
    hosturl = production
else:
    hosturl = development

def send_cmd (wave_id, cmd = "l"):
    r1 = urllib2.urlopen (hosturl + "api.php?get_data=1&wave_id=" + wave_id +
                          "&cmd=" + cmd)

    decjson = simplejson.load (r1)

    return decjson

def start (wave_id, game_name = "zork1"):
    r1 = urllib2.urlopen (hosturl + "api.php?start_game="
                          + game_name + "&wave_id=" + wave_id)

    decjson = simplejson.load (r1)
    
    return decjson

def game_list ():
    r1 = urllib2.urlopen (hosturl + "api.php?list_avail_games=1")
    
    decjson = simplejson.load (r1)

    return decjson

