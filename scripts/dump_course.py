"""
* dump_course.py
"""

import context
from canvasapi import Canvas
import pdb
import json
from pathlib import Path
import os

import requests
import logging
import json
from e340py.utils import login_courses, start_logging
import re
assignnum=re.compile('.*Assignment\s(\d+).*')

def flatten(module_list):
    """
    Given a list of modules return a list of dictionaries of all module items
    """
    outlist=dict()
    for module in module_list:
        outlist[module.id]=dict(name=module.name,items=[])
        items=module.get_module_items()
        for an_item in items:
            outlist[module.id]['items'].append(json.loads(an_item.to_json()))
    return outlist

def get_assignments(course_name):
    canvas, keep = login_courses()
    course=canvas.get_course(keep[course_name])
    assignments = list(course.get_assignments())
    debug = False
    if debug:
        requests_log = start_logging()

    #pdb.set_trace()
    #
    # find all modules in cource
    #
    import pprint
    stars='*'*20
    published={}
    print('here we go')
    for item in assignments:
        if item.published:
            print(item.name)
            out=assignnum.match(item.name)
            try:
                key=int(out.groups(1)[0])
                published[key]=item
            except AttributeError:
                pass
            # print(f"\n{stars}\n")
            # pprint.pprint(item)
            # print(f"\n{stars}\n")
    return published

def make_parser():
    """
    set up the command line arguments needed to call the program
    """
    linebreaks = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        formatter_class=linebreaks, description=__doc__.lstrip())
    parser.add_argument('fsc_file', type=str, help='name of fsc file')
    parser.add_argument('canvas_file', type=str, help='name of canvas file')
    return parser

def main(args=None):
    """
    args: optional -- if missing then args will be taken from command line
          or pass [h5_file] -- list with name of h5_file to open
    """
    import context
    print(
    Path('a301_classlist.json')
    class_dict = json.load
    parser = make_parser()
    args = parser.parse_args(args)
    course_name='a301'
    published=get_assignments(course_name)
    test=list(published[7].get_submissions())
    pdb.set_trace()

if __name__ == "__main__":
    main()

pdb.set_trace()
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










