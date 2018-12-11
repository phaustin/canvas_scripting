#
# get the canvas api token
#
import os
from canvasapi import Canvas
from pathlib import Path
import json
from http.client import HTTPConnection
import logging

def start_logging():
   # Enabling debugging at http.client level (requests->urllib3->http.client)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    HTTPConnection.debuglevel = 1

    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def login_courses():
    my_home=Path(os.environ['HOME'])
    full_path=my_home / Path('.canvas.json')
    with open(full_path,'r') as f:
        secret_dict=json.load(f)
    token=secret_dict['token']
    #
    # set up short names for canvas courses
    #
    API_URL = "https://canvas.ubc.ca"
    # Canvas API key
    API_KEY = token
    nicknames={'a301':'ATSC 301 Atmospheric Radiation and Remote Sensing',
               'e340':'EOSC 340 101 Global Climate Change',
               'box':'Philip_Sandbox'}
    canvas = Canvas(API_URL, API_KEY)
    courses=canvas.get_courses()
    keep=dict()
    for item in courses:
        for shortname,longname in nicknames.items():
            if item.name.find(longname) > -1:
                keep[shortname]=item.id
    return canvas,keep
