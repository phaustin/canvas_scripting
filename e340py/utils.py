from collections import namedtuple, defaultdict
import pandas as pd
import numpy as np
from collections import defaultdict
import pdb

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


def login_courses(canvas_site='live'):
    my_home=Path(os.environ['HOME'])
    full_path=my_home / Path('.canvas.json')
    with open(full_path,'r') as f:
        secret_dict=json.load(f)
    sites={'test':{'token':'test_token',
             'url':'Https://ubc.test.instructure.com'},
           'live':{'token':'live_token',
             'url':'https://canvas.ubc.ca'}}
    token=secret_dict[sites[canvas_site]['token']]
    #
    # set up short names for canvas courses
    #
    API_URL = sites[canvas_site]['url']
    print(f'logging into {API_URL}')
    # Canvas API key
    API_KEY = token
    nicknames={'a301':'ATSC 301 Atmospheric Radiation and Remote Sensing-2018-09',
               'e340':'EOSC 340 101 Global Climate Change-2018-09',
               'box':'Philip_Sandbox'}
    canvas = Canvas(API_URL, API_KEY)
    courses=canvas.get_courses()
    all_courses=[(item.id,item.name,item.start_at) for item in courses]
    #print(f'here are the courses: {all_courses}')
    keep=dict()
    for theid,thename,the_date in all_courses:
        try:
            year,month,rest=the_date.split('-')
            full_name=f"{thename}-{year}-{month}"
        except AttributeError:
            full_name=f"{thename}"
        for shortname,longname in nicknames.items():
            if full_name.find(longname) > -1:
                keep[shortname]=theid
                print(f"hit {shortname} {the_date}")
                print(f"{full_name.find(longname)} -- {full_name} -- {longname}")
    return canvas,keep
