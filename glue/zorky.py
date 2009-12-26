from waveapi import events
from waveapi import model
from waveapi import robot

from zorkyconn import *

NAME = "playzorky"
ROOT = "http://%s.appspot.com" % NAME

title = ""

def add_blip (context, string):
    new_blip = context.GetRootWavelet().CreateBlip()
    new_blip.GetDocument().SetText (string)

def self_added (properties, context):
    initial_string = start (context.GetRootWavelet().GetWaveId())
    add_blip (context, "Playing Zork\n\n%s" % initial_string)

def blip_submitted (properties, context):
    blip = context.GetBlipById (properties["blipId"])
#    all_blips = context.GetBlipById(context.GetRootWavelet().GetRootBlipId()).GetChildBlipIds()
    text = blip.GetDocument().GetText()
    annos = blip.GetAnnotations()
    if text[0] == ">":
        struck = False
        for a in annos:
            if a.name == "style/textDecoration" and a.value == "line-through" \
               and a.range.start == 0:
                struck = True
        if not struck:
            command = (text.split ("\n")[0])[1:].strip()
            add_blip (context, str(send_cmd (context.GetRootWavelet().GetWaveId(),
                                         command)))


if __name__ == "__main__":

    self_robot = robot.Robot (NAME,
                           image_url="%s/assets/icon.png" % ROOT,
                           version="1",
                           profile_url=ROOT)

    self_robot.RegisterHandler (events.WAVELET_SELF_ADDED, self_added)
    self_robot.RegisterHandler (events.BLIP_SUBMITTED, blip_submitted)

    self_robot.Run ()
