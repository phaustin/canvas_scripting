from collections import namedtuple, defaultdict
import pandas as pd
import numpy as np

def make_tuple(in_dict,tupname='values'):
    """
    make a named tuple from a dictionary

    Parameters
    ==========

    in_dict: dictionary
         Any python object with key/value pairs

    tupname: string
         optional name for the new namedtuple type

    Returns
    =======

    the_tup: namedtuple
          named tuple with keys as attributes
    """
    the_tup = namedtuple(tupname, in_dict.keys())
    the_tup = the_tup(**in_dict)
    return the_tup

def stringify_column(df,id_col=None):
    """
    turn a column of floating point numbers into characters

    Parameters
    ----------

    df: dataframe
        input dataframe from quiz or gradebook
    id_col: str
        name of student id column to turn into strings 
        either 'SIS User ID' or 'ID' for gradebook or
        'sis_id' or 'id' for quiz results

    Returns
    -------

    modified dataframe with ids turned from floats into strings
    """
    the_ids = df[id_col].values.astype(np.int)
    index_vals = [f'{item:d}' for item in the_ids]
    df[id_col]=index_vals
    return pd.DataFrame(df)

def clean_id(df,id_col=None):
    """
    give student numbers as floating point, turn
    into 8 character strings, dropping duplicate rows
    in the case of multiple attempts

    Parameters
    ----------

    df: dataframe
        input dataframe from quiz or gradebook
    id_col: str
        name of student id column to turn into strings 
        either 'SIS User ID' for gradebook or
        'sis_id'  quiz results
    
    Returns
    -------

    modified dataframe with duplicates removed and index set to 8 character
    student number
    """
    stringify_column(df,id_col)
    df=df.set_index(id_col,drop=False)
    df.drop_duplicates(id_col,keep='first',inplace=True)
    return pd.DataFrame(df)


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
    return requests_log


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
