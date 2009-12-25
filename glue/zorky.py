from waveapi import events
from waveapi import model
from waveapi import robot

NAME = "playzorky"
ROOT = "http://%s.appspot.com" % NAME

title = ""

def add_blip (context, string):
    context.GetRootWavelet().CreateBlip().GetDocument().SetText (string)

def self_added (properties, context):
    title = context.GetRootWavelet().GetTitle ()
    add_blip (context, "The current title is: %s" % title) 

def title_changed (properties, context):
    old_title = title
    title = context.GetRootWavelet().GetTitle ()
    add_blip (context, "The new title of this wavelet is: %s (was %s)"
              % (title, old_title))

if __name__ == "__main__":
    self_robot = robot.Robot (NAME,
                           image_url="%s/assets/icon.png" % ROOT,
                           version="1",
                           profile_url=ROOT)

    self_robot.RegisterHandler (events.WAVELET_SELF_ADDED, self_added)
    self_robot.RegisterHandler (events.BLIT_SUBMITTED, blip_submitted)

    self_robot.Run ()
