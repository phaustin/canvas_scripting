import json
import logging
import os
import pdb
from collections import defaultdict
from collections import namedtuple
from http.client import HTTPConnection
from pathlib import Path

import numpy as np
import pandas as pd
from canvasapi import Canvas

logging.captureWarnings(True)  # [noqa]


def merge_two(df_left, df_right):
    df_return = pd.merge(
        df_left, df_right, how="left", left_index=True, right_index=True, sort=False
    )
    return pd.DataFrame(df_return, copy=True)


def make_tuple(in_dict, tupname="values"):
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


def vector_to_str(the_floats):
    int_vals = the_floats.astype(np.int)
    string_vals = [f"{item:d}" for item in int_vals]
    return string_vals


def vector_to_int(the_floats):
    int_vals = the_floats.astype(np.int)
    return int_vals


def stringify_df_column(df, id_col=None):
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
    string_vals = vector_to_str(df[id_col].values)
    df[id_col] = string_vals
    return pd.DataFrame(df)


def clean_id(df, id_col=None, drop=True):
    """
    give student numbers as floating point, turn
    into ints and set index

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
    the_id_vector = df[id_col].values
    the_id_ints = [int(item) for item in the_id_vector]
    df[id_col] = the_id_ints
    df.set_index(id_col, drop=drop, inplace=True)
    return pd.DataFrame(df, copy=True)


#
# get the canvas api token
#


def start_logging():
    # Enabling debugging at http.client level (requests->urllib3->http.client)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    HTTPConnection.debuglevel = 1

    logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    return requests_log


def login_courses(canvas_site="live"):
    my_home = Path(os.environ["HOME"])
    full_path = my_home / Path(".canvas.json")
    with open(full_path, "r") as f:
        secret_dict = json.load(f)
    sites = {
        "test": {"token": "test_token", "url": "Https://ubc.test.instructure.com"},
        "live": {"token": "live_token", "url": "https://canvas.ubc.ca"},
    }
    token = secret_dict[sites[canvas_site]["token"]]
    #
    # set up short names for canvas courses
    #
    API_URL = sites[canvas_site]["url"]
    print(f"logging into {API_URL}")
    # Canvas API key
    API_KEY = token
    nicknames = {
        "a301": ("ATSC 301 Atmospheric Radiation and Remote Sensing-2018-09", 9243),
        "e340t1": ("EOSC 340 101 Global Climate Change-2018-09", 6084),
        "box": ("Philip_Sandbox", 3188),
        "e213": ("EOSC 213 201 Computational Methods in Geological Engineering", 19626),
        "e340t2": ("EOSC 340 201 Global Climate Change", 19632),
    }
    canvas = Canvas(API_URL, API_KEY)
    courses = canvas.get_courses()
    all_courses = [(item.id, item.name, item.start_at) for item in courses]
    keep = dict()
    for theid, thename, the_date in all_courses:
        try:
            year, month, rest = the_date.split("-")
            full_name = f"{thename}-{year}-{month}"
        except AttributeError:
            full_name = f"{thename}"
        for shortname, (longname, courseid) in nicknames.items():
            if courseid == theid:
                keep[shortname] = theid
                print(f"{shortname}, {theid}, {full_name[:80]}")
    return canvas, keep
