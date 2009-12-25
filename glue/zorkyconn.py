#! /usr/bin/env python

import httplib2, urllib

#hosturl = "http://willisson.org/zorky.html"
hosturl = "http://rhino.local:9001/"

def sendcmd (cmd):
    safecmd = urllib.quote (cmd)
    tar = hosturl + "?" + safecmd
    tar = hosturl
    h = httplib2.Http (".cache")
    resp, content = h.request (tar, "GET")

    print h, resp, content
