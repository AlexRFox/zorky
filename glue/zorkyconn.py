#! /usr/bin/env python

import httplib2, urllib, simplejson

#hosturl = "http://willisson.org/zorky.html"
hosturl = "http://rhino.local:9001/"

def sendcmd (cmd):
    safecmd = urllib.quote (cmd)
    tar = hosturl + "?" + safecmd
    tar = hosturl
    h = httplib2.Http (".cache")
    resp, content = h.request (tar, "GET")

    content = '{"menu": {   "id": "file",   "value": "File",   "popup": {     "menuitem": [       {"value": "New", "onclick": "CreateNewDoc()"},       {"value": "Open", "onclick": "OpenDoc()"},       {"value": "Close", "onclick": "CloseDoc()"}     ]   } }}'

    decjson = simplejson.loads (content)

    return decjson

print sendcmd ("get all in bag")
