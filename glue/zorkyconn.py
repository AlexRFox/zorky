#! /usr/bin/env python

import httplib, simplejson, urllib, urllib2

production = "http://zorky.willisson.org/"
dev0 = "http://zorkydev.willisson.org/"
dev1 = "http://rhino.local:9001/"
dev2 = "http://localhost:9001/"

hosturl = dev2

def send_cmd (wave_id, cmd = "l"):
    params = urllib.urlencode ({"get_data": 1, "wave_id": wave_id, "cmd": cmd})

    r1 = urllib2.urlopen (hosturl + "api.php?" + params)

    decjson = simplejson.load (r1)

    data = decjson['display'].split ("\n\n", 1)

    roomname = data[0][:45].strip ()
    try:
        score = int (data[0][51:61].strip ())
    except ValueError:
        score = 0

    try:
        moves = int (data[0][67:])
    except ValueError:
        moves = 0

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
    try:
        score = int (data[0][51:61].strip ())
    except ValueError:
        score = 0

    try:
        moves = int (data[0][67:])
    except ValueError:
        moves = 0
        
    content = data[1][:-2]

    output = {'roomname': roomname, 'score': score, 'moves': moves,
              'content': content}

    return output

def game_list ():
    params = urllib.urlencode ({"list_avail_games": 1})

    r1 = urllib2.urlopen (hosturl + "api.php?" + params)
    
    decjson = simplejson.load (r1)

    return decjson

def check_saves ():
    params = urllib.urlencode ({"list_saved_games": 1, "wave_id": wave_id})

    r1 = urllib2.urlopen (hosturl + "api.php?" + params)

    decjson = simplejson.load (r1)

    return decjson
