"""

add_points -- modify a gradebook column to account for comments and hours worked

to run:

cd /Users/phil/Nextcloud/e340_coursework/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades

quiz 22 example:

add_points file_names.json day22_quiz_results.csv -c q 22

the result is a file called "q_22_upload.csv" which replaces the day quiz results

assignment 1 example:

add_points file_names.json assignment_1_results.csv -c a 1

"""
import argparse
import json
import os
import pdb
import re

import numpy as np
import pandas as pd

from .utils import clean_id
from .utils import make_tuple
from .utils import stringify_column


def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks, description=descrip)
    parser.add_argument("json_file", type=str, help="input json file with filenames")
    parser.add_argument("-c", "--column", nargs="+", help="quiz/assignment column")
    parser.add_argument("quiz_file", type=str, help="quiz file for the day")
    return parser


# -------------
# use these regular expressions to identify quizzes and assignments and to find
# the hours and comments questions in an individual quiz/assignment
# -------------

mid_re = re.compile(r".*Midterm\s(\d)\s-\sIndividual")
day_re = re.compile(r".*Day\s(\d+).*")
assign_re = re.compile(r".*Assign.*\s(\d+).*")
hours_re = re.compile(r".*How much time did you spend.*")
ques_re = re.compile(r".*something you found confusing or unclear.*")


def boost_grade(row, quiztype="q"):
    """
     give a row of a dataframe pull the comment and the hours worked and
     calculate additiona points

    Parameters
    ----------

    row: Pandas series
        row of dataframe passed by pandas.apply

    quiztype: str
        either 'q' for quiz or 'a' for assignment
        quiz gets a boost for both comments and hours worked
        assignment only for hours worked
    """
    comment_points = 0
    hours_points = 0
    if quiztype == "q":
        try:
            len_comments = len(row.comments)
        except TypeError:  # nan
            len_comments = 0
        if len_comments > 0 and row.comments != "none":
            comment_points = 1.0
        else:
            comment_points = 0.0
    if row.hours > 0.0 and row.hours < 50:
        hours_points = 0.5
    out = comment_points + hours_points
    # print(f'boost: {out} {comment_points} {hours_points}')
    if np.isnan(out):
        out = 0.0
    return out


def main(the_args=None):
    #
    # make_parser uses sys.args by default,
    # the_args can be set during code testing
    #
    parser = make_parser()
    args = parser.parse_args()
    quiztype, quiznum = list(args.column)
    with open(args.json_file, "r") as f:
        name_dict = json.load(f)
    n = make_tuple(name_dict)
    # ----------------------
    # read in the gradebook
    # ----------------------
    with open(n.grade_book, "r", encoding="utf-8-sig") as f:
        df_gradebook = pd.read_csv(f)
    df_gradebook = df_gradebook.fillna(0)
    # -----------------
    # drop the mute/not mute row
    # and save points possbile for final write
    # -----------------
    df_gradebook = df_gradebook.drop([0])
    points_possible = df_gradebook.iloc[0, :]
    df_gradebook = clean_id(df_gradebook, id_col="SIS User ID")
    df_gradebook = stringify_column(df_gradebook, id_col="ID")
    df_gradebook.iloc[0, :] = points_possible
    grade_cols = list(df_gradebook.columns.values)
    dumplist = []
    # --------------------
    # get all assignment and quiz column headers from gradebook
    # and save in grade_col_dict
    # ---------------------
    for item in grade_cols:
        day_out = day_re.match(item)
        assign_out = assign_re.match(item)
        if day_out:
            daynum = ("q", day_out.groups(1)[0])
            dumplist.append((daynum, item))
        elif assign_out:
            assignnum = ("a", assign_out.groups(1)[0])
            dumplist.append((assignnum, item))
        else:
            continue

    grade_col_dict = dict(dumplist)
    # -----------------------------
    # read the quiz/assignment results into a dataframe
    # -----------------------------
    with open(args.quiz_file, "r", encoding="utf-8-sig") as f:
        df_quiz_result = pd.read_csv(f)
    df_quiz_result = stringify_column(df_quiz_result, "id")
    df_quiz_result.fillna(0.0, inplace=True)
    df_quiz_result = clean_id(df_quiz_result, id_col="sis_id")
    quiz_cols = list(df_quiz_result.columns.values)
    # --------------------
    # find the hours column
    # --------------------
    for col in quiz_cols:
        hours_string = None
        match = hours_re.match(col)
        if match:
            Hours_string = col  # noqa
            break
    bad_hours_ids = df_quiz_result[df_quiz_result[hours_string] == 1000.0].index
    df_quiz_result.loc[bad_hours_ids, hours_string] = 0.0
    score_column = grade_col_dict[(quiztype, quiznum)]
    df_gradebook.loc[bad_hours_ids, score_column] -= 0.5
    # -------------
    # make a minimal copy of the quiz dataframe to work with
    # add hours and (if quiz not assignment) comments columns
    # -------------
    comment_string = None
    df_small_frame = pd.DataFrame(df_quiz_result.iloc[:, :4])
    ques_hours = df_quiz_result[hours_string]
    hours_list = []
    for item in ques_hours:
        try:
            out = float(item)
        except ValueError:
            out = 0
        hours_list.append(out)
    df_small_frame["hours"] = hours_list
    # --------------
    # if it's a quiz instead of an assignment, add the comments
    # --------------
    if quiztype == "q":
        for col in quiz_cols:
            match = ques_re.match(col)
            if match:
                comment_string = col
                break
        ques_scores = df_quiz_result[comment_string]
        df_small_frame["comments"] = ques_scores
    # -----------------
    # apply the boost_grade function to calculate bonus points for hours and comments
    # ----------------
    df_small_frame["boost"] = df_small_frame.apply(
        boost_grade, axis=1, quiztype=quiztype
    )
    df_small_frame = pd.DataFrame(df_small_frame[["boost"]])
    # ----------------
    # merge the single column df_small_frame onto the gradebook dataframe
    # ----------------
    mergebook = pd.merge(
        df_gradebook,
        df_small_frame,
        how="left",
        left_index=True,
        right_index=True,
        sort=False,
    )
    new_score = mergebook[score_column].values + mergebook["boost"].values
    mergebook[score_column] = new_score
    # ---------------------
    # now make a new gradebook to upload the new_score column
    # this gradebook has the quiz score header so canvas will overwrite
    # ---------------------
    mandatory_columns = list(mergebook.columns[:5])
    mandatory_columns = mandatory_columns + [score_column]
    df_upload = pd.DataFrame(mergebook[mandatory_columns])
    for item in [1, 2, 3, 4]:
        points_possible[item] = " "
    df_upload.iloc[0, :] = points_possible[mandatory_columns]
    total_points = points_possible[score_column]
    # pdb.set_trace()
    hit = df_upload[score_column] > total_points
    df_upload.loc[hit, score_column] = total_points
    new_name = f"{quiztype}_{quiznum}_upload.csv"
    with open(new_name, "w", encoding="utf-8-sig") as f:
        df_upload.to_csv(f, index=False, sep=",")


if __name__ == "__main__":
    main()
