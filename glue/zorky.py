from waveapi import events
from waveapi import model
from waveapi import robot

import urllib2

from zorkyconn import *

def start():
    return "The <i>Great</i> Underground Adventure"

NAME = "playzorky"
ROOT = "http://%s.appspot.com" % NAME

title = ""

def add_blip (context, string):
    context.GetRootWavelet().CreateBlip().GetDocument().SetText (string)

def self_added (properties, context):
    initial_string = start ()
    add_blip (context, "*Playing Zork*\n\n%s" % initial_string)

def blip_submitted (properties, context):
    blip = context.GetBlipById (properties["blipId"])
    text = blip.GetDocument().GetText()
    if text[0] == ">":
        command = (text.split ("\n")[0])[1:].strip()
        add_blip (context, urllib2.urlopen ("http://www.google.com"))
    else:
        add_blip (context, "I did not recognize that line")

if __name__ == "__main__":

    self_robot = robot.Robot (NAME,
                           image_url="%s/assets/icon.png" % ROOT,
                           version="1",
                           profile_url=ROOT)

    self_robot.RegisterHandler (events.WAVELET_SELF_ADDED, self_added)
    self_robot.RegisterHandler (events.BLIP_SUBMITTED, blip_submitted)

    self_robot.Run ()
