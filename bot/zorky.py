from waveapi import events
from waveapi import model
from waveapi import robot
import waveapi.document

import conn

NAME = "playzorky"
ROOT = "http://%s.appspot.com" % NAME

title = ""

def send_cmd (wave_id, command):
    "Make conn.send_cmd()'s output nice"

    response = conn.send_cmd (wave_id, command)

    return response['display']

def start (wave_id, game_name):
    "Make conn.start()'s output nice"

    response = conn.start (wave_id, game_name)

    return response['display']

def end (wave_id):
    "Make conn.end()'s output nice"

    response = conn.end (wave_id)
    
    return response['display']

def game_list ():
    "Make conn.game_list()'s output nice"

    games = conn.game_list()['names']
    games = map (lambda s: s[:-3], games)
    games.sort()

    return ("Possible games (choose one by starting a blip with \"/game " +
            "<name>\"):\n" + '\n'.join (games))

def save_list (wave_id):
    "Make conn.check_saves()'s output nice"

    return conn.check_saves (wave_id)

def struck (annos):
    struck_out = False
    for a in annos:
        if a.name == "style/textDecoration" and a.value == "line-through" \
               and a.range.start == 0:
            struck_out = True
    return struck_out

def add_blip (context, string, bold_first_line=False):
    new_blip = context.GetRootWavelet().CreateBlip()
    new_blip.GetDocument().SetText (str(string))

    if bold_first_line:
        new_blip.GetDocument().SetAnnotation (waveapi.document.Range
                                              (0, len(string.split('\n')[0])),
                                              "style/fontWeight", "bold")

def zorkyhelp ():
    "Help docs"
    return "Commands to dfrotz must begin with > (i.e. > n). Zorky will assume any newly created or edited blips with a > in it have a command, and ship everything after the > to dfrotz, unless the line is struck (i.e. has a line through it)\n\nCommands to bot:\nStarting a game: /start <game>, /play <game>, /game <game> (i.e. /start zork1)\nEnding a game: /quit, /end\nTo list available games: /listgames\nTo list available save games: /listsaves\n"

def self_added (properties, context):
    root_text = context.GetBlipById(context.GetRootWavelet().GetRootBlipId()).GetDocument().GetText()

    game = "list"
    for line in root_text.split("\n"):
        if line.lower().find ("/game") != -1 or line.lower().find ("/play") != -1:
            game = line[5:].strip()
            break
        elif line.lower().find ("/list") != -1:
            game = "list"
            break

    blipstr = "Type /help to see available commands\n\n"

    if game == "list":
        blipstr += game_list ()
        add_blip (context, blipstr)
    else:
        initial_string = start (context.GetRootWavelet().GetWaveId(), game)
        blipstr += "Playing %s\n\n%s" % (game, initial_string)
        add_blip (context, blipstr)

def blip_submitted (properties, context):
    blip = context.GetBlipById (properties["blipId"])
#    all_blips = context.GetBlipById(context.GetRootWavelet().GetRootBlipId()).GetChildBlipIds()
    text = blip.GetDocument().GetText()
    annos = blip.GetAnnotations()
    wave_id = context.GetRootWavelet().GetWaveId()
    if text[0] == ">":
        if not struck (annos):
            command = (text.split ("\n")[0])[1:].strip()
            response = send_cmd (wave_id, command)
            add_blip (context, "> %s\n\n%s" % (command, response), True)
    elif text[0] == "/":
        if not struck (annos):
            command = (text.split ("\n")[0])[1:].strip()
            if command[:4] == "game" or command[:4] == "play" \
                    or command[:5] == "start":
                game = command[5:].strip()
                initial_string = start (wave_id, game)
                add_blip (context, "Playing %s\n\n%s" % (game, initial_string), True)
            elif command[:4] == "help":
                add_blip (context, zorkyhelp ())
            elif command[:9] == "listgames":
                add_blip (context, game_list ())
            elif command[:9] == "listsaves":
                add_blip (context, save_list (wave_id))
            elif command[:3] == "end" or command[:4] == "quit":
                add_blip (context, end (wave_id), True)

if __name__ == "__main__":

    self_robot = robot.Robot (NAME,
                           image_url="%s/assets/icon.png" % ROOT,
                           version="1",
                           profile_url=ROOT)

    self_robot.RegisterHandler (events.WAVELET_SELF_ADDED, self_added)
    self_robot.RegisterHandler (events.BLIP_SUBMITTED, blip_submitted)

    self_robot.Run ()
