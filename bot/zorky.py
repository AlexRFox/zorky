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

    return response['content']

def start (wave_id, game_name):
    "Make conn.start()'s output nice"

    response = conn.start (wave_id, game_name)

    if len (response['error']):
        return response['error']

    return response['content']

def game_list ():
    "Make conn.game_list()'s output nice"

    games = conn.game_list()['names']
    games = map (lambda s: s.strip(".z5"), games)
    games.sort()

    return ("Possible games (choose one by starting a blip with \"/game " +
            "<name>\" or \"/play <name> \"):\n" + '\n'.join (games))

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

    if game == "list":
        add_blip (context, game_list())
    else:
        initial_string = start (context.GetRootWavelet().GetWaveId(), game)
        add_blip (context, "Playing %s\n\n%s\n>" % (game, initial_string), True)

def blip_submitted (properties, context):
    blip = context.GetBlipById (properties["blipId"])
#    all_blips = context.GetBlipById(context.GetRootWavelet().GetRootBlipId()).GetChildBlipIds()
    text = blip.GetDocument().GetText()
    annos = blip.GetAnnotations()
    if text[0] == ">":
        if not struck (annos):
            command = (text.split ("\n")[0])[1:].strip()
            response = send_cmd (context.GetRootWavelet().GetWaveId(), command)
            add_blip (context, "> %s\n\n%s\n>" % (command, response), True)
    elif text[0] == "/":
        if not struck (annos):
            command = (text.split ("\n")[0])[1:].strip()
            if command[:4] == "game" or command[:4] == "play":
                game = command[5:].strip()
                initial_string = start (context.GetRootWavelet().GetWaveId(),
                                        game)
                add_blip (context, "Playing %s\n\n%s\n>" % (game, initial_string), True)
            
if __name__ == "__main__":

    self_robot = robot.Robot (NAME,
                           image_url="%s/assets/icon.png" % ROOT,
                           version="1",
                           profile_url=ROOT)

    self_robot.RegisterHandler (events.WAVELET_SELF_ADDED, self_added)
    self_robot.RegisterHandler (events.BLIP_SUBMITTED, blip_submitted)

    self_robot.Run ()
