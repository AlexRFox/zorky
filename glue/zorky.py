from waveapi import events
from waveapi import model
from waveapi import robot

import re

from zorkyconn import *

NAME = "playzorky"
ROOT = "http://%s.appspot.com" % NAME

title = ""

def struck (annos):
    struck_out = False
    for a in annos:
        if a.name == "style/textDecoration" and a.value == "line-through" \
               and a.range.start == 0:
            struck_out = True
    return struck_out

def add_blip (context, string):
    new_blip = context.GetRootWavelet().CreateBlip()
    new_blip.GetDocument().SetText (string)

def self_added (properties, context):
    root_text = context.GetBlipById(context.GetRootWavelet().GetRootBlipId()).GetDocument().GetText()
    game = "list"
    for line in root_text.split("\n"):
        if line.lower().find ("Game:") != -1:
            game = line[5:].strip()

    if game == "list":
        add_blip (game_list())
    else:
        initial_string = start (context.GetRootWavelet().GetWaveId(), game)
        add_blip (context, "Playing %s\n\n%s" % (game, initial_string))

def blip_submitted (properties, context):
    blip = context.GetBlipById (properties["blipId"])
#    all_blips = context.GetBlipById(context.GetRootWavelet().GetRootBlipId()).GetChildBlipIds()
    text = blip.GetDocument().GetText()
    annos = blip.GetAnnotations()
    if text[0] == ">":
        if not struck (annos):
            command = (text.split ("\n")[0])[1:].strip()
            add_blip (context, str(send_cmd (context.GetRootWavelet().GetWaveId(),
                                         command)))
    elif text[0] == "[":
        if not struck (annos):
            command = (text.split ("\n")[0])[1:].strip()
            
if __name__ == "__main__":

    self_robot = robot.Robot (NAME,
                           image_url="%s/assets/icon.png" % ROOT,
                           version="1",
                           profile_url=ROOT)

    self_robot.RegisterHandler (events.WAVELET_SELF_ADDED, self_added)
    self_robot.RegisterHandler (events.BLIP_SUBMITTED, blip_submitted)

    self_robot.Run ()
