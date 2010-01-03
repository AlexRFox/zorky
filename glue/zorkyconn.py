#! /usr/bin/env python

import httplib, simplejson, urllib, urllib2

production = "http://zorky.willisson.org/api.php?"
dev = "http://localhost:9001/api.php?"

hosturl = dev

def send_cmd (wave_id, cmd = "l"):
    params = urllib.urlencode ({"get_data": 1, "wave_id": wave_id, "cmd": cmd})

    r1 = urllib2.urlopen (hosturl + params)

    decjson = simplejson.load (r1)

#    data = decjson['display'].split ("\n\n", 1)

#    roomname = data[0][:45].strip ()
#    try:
#        score = int (data[0][51:61].strip ())
#    except ValueError:
    #     score = 0

    # try:
    #     moves = int (data[0][67:])
    # except ValueError:
    #     moves = 0

    # content = data[1][:-2]

    # output = {'roomname': roomname, 'score': score, 'moves': moves,
    #           'content': content}

#    return output

    return decjson

def start (wave_id, game_name = "zork1"):
    params = urllib.urlencode ({"check_wave_id": wave_id})
    r1 = urllib2.urlopen (hosturl + params)
    decjson = simplejson.load (r1)
    if (decjson['status'] == 0):
        output = {'error': "wave_id in use, please end current" + \
                      " game before starting a new one"}
        return output

    params = urllib.urlencode ({"start_game": game_name, "wave_id": wave_id})
    
    r1 = urllib2.urlopen (hosturl + params)

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

def end (wave_id):
    content = send_cmd (wave_id, "quit")

    params = urllib.urlencode ({"end_game": wave_id})
    r1 = urllib2.urlopen (hosturl + params)
    decjson = simplejson.load (r1)

    output = {'display': "Ignore any confirmation requests\n\n" \
                  + content['display'] + "\n\nGame ended\n"}

    return output

def game_list ():
    params = urllib.urlencode ({"list_avail_games": 1})

    r1 = urllib2.urlopen (hosturl + params)
    
    decjson = simplejson.load (r1)

    return decjson

def check_saves ():
    params = urllib.urlencode ({"list_saved_games": 1, "wave_id": wave_id})

    r1 = urllib2.urlopen (hosturl + params)

    decjson = simplejson.load (r1)

    return decjson
