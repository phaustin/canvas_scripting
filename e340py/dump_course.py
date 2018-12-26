"""
* dump_course.py
"""
import argparse
import json
import logging
import os
import pdb
import re
from pathlib import Path

import context
import requests
from canvasapi import Canvas

from .utils import login_courses
from .utils import start_logging


def flatten(module_list):
    """
    Given a list of modules return a list of dictionaries of all module items
    """
    outlist = dict()
    for module in module_list:
        outlist[module.id] = dict(name=module.name, items=[])
        items = module.get_module_items()
        for an_item in items:
            outlist[module.id]["items"].append(json.loads(an_item.to_json()))
    return outlist


def get_course(course_name):
    canvas, course_ids = login_courses()
    course = canvas.get_course(course_ids[course_name])
    return course


def get_assignments(course_name):
    if isinstance(course_name, str):
        canvas, course_ids = login_courses()
        course = canvas.get_course(course_ids[course_name])
    else:
        course = course_name
    assignments = list(course.get_assignments(frozen_attributes=["title"]))
    print(f"found {len(assignments)} assignments")
    debug = False
    if debug:
        requests_log = start_logging()  # noqa
    out = [item for item in assignments if item.published]
    print(f"returning {len(out)} published assignments")
    return out


def make_parser():
    """
    set up the command line arguments needed to call the program
    """
    linebreaks = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        formatter_class=linebreaks, description=__doc__.lstrip()
    )
    parser.add_argument("fsc_file", type=str, help="name of fsc file")
    parser.add_argument("canvas_file", type=str, help="name of canvas file")
    return parser


def main(args=None):
    """
    args: optional -- if missing then args will be taken from command line
          or pass [h5_file] -- list with name of h5_file to open
    """

    parser = make_parser()
    args = parser.parse_args(args)


if __name__ == "__main__":
    main()

# # modules=course.get_modules()
# # module_list=flatten(modules)

# out_file='sandbox.json'
# with open(out_file,'w') as f:
#     json.dump(module_list,f,indent=4)


# #
# # change the module name and write back tuo canvas
# #
# # print(f'found module: {assign_module}')
# # assign_module.edit(module={'name':'assignphaVV','published':True})
# # new_module=course.get_module(assign_module.id)
# # star10='*'*10
# # print(f'\n{star10}\nchanged module name to {new_module.name}\n{star10}\n')
# # all_items=list(new_module.get_module_items())
# # out=dict(courseid=course.id,moduleid=assign_module.id)
# #pdb.set_trace()
