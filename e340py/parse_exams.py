"""
  test_grades.py
"""
import argparse
import json
import os
import pdb
import re
from pathlib import Path

import pandas as pd

from .utils import clean_id
from .utils import make_tuple
from .utils import stringify_df_column


def get_col_names(day_re, assign_re, grade_cols):
    # --------------------
    # get all assignment and quiz column headers from gradebook
    # and save in grade_col_dict
    # ---------------------
    dumplist = []
    for item in grade_cols:
        day_out = day_re.match(item)
        assign_out = assign_re.match(item)
        if day_out:
            daynum = f"q-{day_out.groups(1)[0]}"
            dumplist.append((daynum, item))
        elif assign_out:
            assignnum = f"a-{assign_out.groups(1)[0]}"
            dumplist.append((assignnum, item))
        else:
            continue
    grade_col_dict = dict(dumplist)
    return grade_col_dict


def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks, description=descrip)
    parser.add_argument("json_file", type=str, help="input json file with filenames")
    return parser


def grade_group(df_groupraw):
    ids = ["STUDENT ID #1", "STUDENT ID #2", "STUDENT ID #3", "STUDENT ID #4"]
    group_id_list = []
    group_score_list = []
    for index, the_row in df_groupraw.iterrows():
        for a_id in ids:
            try:
                try:
                    the_id = "{:d}".format(int(the_row[a_id]))
                    group_id_list.append(the_id)
                except ValueError:
                    print(f"caught bad id {a_id}")
                    print(f"row={the_row}")
                    continue
            except (TypeError, ValueError):
                raise Exception("bad group id entry")
            percent_score = the_row["Percent Score"]
            group_score_list.append(percent_score)
    out = [{"id": item} for count, item in enumerate(group_id_list)]
    df_group = pd.DataFrame.from_records(out)
    df_group["group_score"] = group_score_list
    return df_group


def main(the_args=None):

    #   mid_re = re.compile(r".*Midterm\s(\d)\s-\sIndividual")
    day_re = re.compile(r".*Day\s(\d+).*")
    assign_re = re.compile(r".*Assign.*\s(\d+).*")
    #    hours_re = re.compile(r".*How much time did you spend.*")
    #    ques_re = re.compile(r".*something you found confusing or unclear.*")

    parser = make_parser()
    args = parser.parse_args()

    with open(args.json_file, "r") as f:
        name_dict = json.load(f)
    n = make_tuple(name_dict)
    # ----------------------
    # read in the gradebook
    # ----------------------
    root_dir = Path(os.environ["HOME"]) / Path(n.data_dir)
    grade_book = root_dir / Path(n.grade_book)
    with open(grade_book, "r", encoding="ISO-8859-1") as f:
        df_gradebook = pd.read_csv(f)
    df_gradebook = df_gradebook.fillna(0)
    #
    # read in the group exam
    #
    root_dir = Path(os.environ["HOME"]) / Path(n.final_dir)

    pdb.set_trace()

    # -----------------
    # drop the mute/not mute row
    # and save points possbile for final write
    # -----------------
    df_gradebook = df_gradebook.drop([0])
    points_possible = df_gradebook.iloc[0, :]
    df_gradebook = clean_id(df_gradebook, id_col="SIS User ID")
    df_gradebook = stringify_df_column(df_gradebook, id_col="ID")
    df_gradebook.iloc[0, :] = points_possible
    grade_cols = list(df_gradebook.columns.values)
    grade_col_dict = get_col_names(day_re, assign_re, grade_cols)
    quiz_list = [item for item in grade_col_dict.keys() if item[0] == "q"]
    assign_list = [item for item in grade_col_dict.keys() if item[0] == "a"]
    rename_dict = dict()
    quiz_list.extend(assign_list)
    quiz_list.sort()
    for key in quiz_list:
        rename_dict[grade_col_dict[key]] = key
    df_gradebook.rename(columns=rename_dict, inplace=True)
    df_gradebook = pd.DataFrame(df_gradebook[quiz_list])

    return df_gradebook


if __name__ == "__main__":
    df_gradebook = main()
