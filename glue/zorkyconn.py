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

    data = decjson['dispay'].split ("\n\n", 1)

    roomname = data[0][:45].strip ()
    score = int (data[0][51:61].strip ())
    moves = int (data[0][67:])
    content = data[1][:-2]

    output = {'roomname': roomname, 'score': score, 'moves': moves,
              'content': content}

    return output

def start (wave_id, game_name = "zork1"):
    params = urllib.urlencode ({"start_game": game_name, "wave_id": wave_id})
    
    r1 = urllib2.urlopen (hosturl + "api.php?" + params)

    decjson = simplejson.load (r1)

    data = decjson['display'].split ("\n\n", 1)

    roomname = data[0][:45].strip ()
    score = int (data[0][51:61].strip ())
    moves = int (data[0][67:])
    content = data[1][:-2]

    output = {'roomname': roomname, 'score': score, 'moves': moves,
              'content': content}

    return output

def game_list ():
    params = urllib.urlencode ({"list_avail_games": 1})

    r1 = urllib2.urlopen (hosturl + "api.php?" + params)
    
    decjson = simplejson.load (r1)

    return decjson
