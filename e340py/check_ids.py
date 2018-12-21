"""
https://stackoverflow.com/questions/32055817/python-fuzzy-matching-fuzzywuzzy-keep-only-best-match
 * check_ids.py

 python check_ids.py  file_list.json

{
    "comment" : "data_dir relative to home directory",
    "program_dir": "/Users/phil/repos/eoas_canvas/scripts",
    "data_dir": "Nextcloud/e340_2018_fall/Exams/midterm1_2018t1/Grades",
    "correction_module_path" : "fix_grades/correct_y2018t1.py",
    "correction_module_name" : "correct_y2018t1",
    "group_file": "grades_group_clean.xlsx",
    "ind_file": "grades_individual_clean.xlsx",
    "grade_book": "2018-10-22T2118_Grades-EOSC340.101.csv",
    "fsc_list": "classlists_2018W_UBC_EOSC_340_101.xls",
    "key_file": "Keys.xlsx",
    "upload_file" :"midterm1_upload.csv",
    "pha_clickers" : "pha_clickers_apr11.csv",
    "finan_dir" : "tbd"
}

"""
from matplotlib import pyplot as plt
import importlib.util
import pyutils
import sys
import os
import numpy as np
from pathlib import Path
import argparse
from fuzzywuzzy import fuzz
import pdb
import json
from e340py.utils import make_tuple, stringify_column, clean_id
from e340py.parse_exams import grade_group
import pandas as pd


def convert_ids(float_id):
    the_id = [f'{int(item):d}' for item in float_id if not np.isnan(item)]
    if len(float_id) != len(the_id):
        print(f'given {len(float_id)} returned {len(the_id)}')
    return the_id

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('file_list',type=str,help='json file with file locatoins')
    return parser

def mark_combined(row):
    group = row['group_score']
    if group < row['ind_score']:
        group = row['ind_score']
    mark = 0.85*row['ind_score'] + 0.15*group
    return mark


def main(the_args=None):
    parser = make_parser()
    args = parser.parse_args(the_args)
    with open(args.file_list,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)
    #
    # get the final individual
    #
    #
    # get the class list
    #
    root_dir = Path(os.environ['HOME']) / Path(n.data_dir)
    module_path= root_dir / Path(n.correction_module_path)
    spec = importlib.util.spec_from_file_location(n.correction_module_name, module_path)
    fix_grades = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fix_grades)
    # Optional; only necessary if you want to be able to import the module
    # by name later.
    # sys.modules[module_name] = module
        
    official_list = root_dir / Path(n.fsc_list)
    with open(official_list,'rb') as f:
        df_fsc=pd.read_excel(f,sheet=None)
    #
    # get the group final
    #
    group_file = root_dir / Path(n.group_file)
    with open(group_file,'rb') as f:
        group_grades=pd.read_excel(f,sheet=None)
    columns=group_grades.columns

    group_ids=[]
    #
    # the group excel file has 4 columns for student ids
    #
    for col in columns[:4]:
        the_ids=convert_ids(group_grades[col])
        group_ids.extend(the_ids)
    #
    # get the individual final
    #
    ind_file = root_dir / Path(n.ind_file)
    with open(ind_file,'rb') as f:
        ind_grades=pd.read_excel(f,sheet=None)
    ind_ids = clean_id(ind_grades, id_col = 'STUDENT ID')
    official_ids= clean_id(df_fsc,id_col='Student Number')
    print(f'number of ind exams: {len(ind_ids)}')
    print(f'number of group exams: {len(group_ids)}')
    #
    # find official ideas that appear
    #
    missing = set(official_ids.index.values) - set(ind_ids.index.values)
    print('\nmissed exam individual\n')
    for number in missing:
        hit = official_ids.index.values==number
        info = official_ids[hit][['Surname','Student Number']].values[0]
        print(*info)

    print('\nmissed group exam\n')    
    missed_group = set(official_ids.index.values) - set(group_ids)
    for number in missed_group:
        hit = official_ids.index.values==number
        info = official_ids[hit][['Surname','Student Number']].values[0]
        print(*info)


    def find_closest(the_id,good_ids):
        score_list=[]
        for choice in good_ids:
            score_list.append(fuzz.ratio(the_id,choice))
        score_array=np.array(score_list)
        max_index=np.argmax(score_array)
        good_choice=good_ids[max_index]
        return good_choice

    print('\nindividual exam: suggest close ids if typos\n')

    for item in ind_ids.index:
        if item not in official_ids.index.values:
            print(f'individ. miss on {item}')
            nearest=find_closest(item,official_ids.index.values)
            print(f'possible value is {nearest}')

    if len(group_ids) > 0:
        print('\nnow group: suggest close ids\n')

    for item in group_ids:
        if item not in official_ids.index.values:
            print(f'group miss on {item}')
            nearest=find_closest(item,official_ids.index.values)
            print(f'possible value is {nearest}')

    df_group=grade_group(group_grades)
    df_group = fix_grades.fix_group(df_group)
    df_ind = pd.DataFrame(ind_ids[['LAST NAME','FIRST NAME','Percent Score']])
    df_ind['id'] = df_ind.index
    new_name_dict={'Percent Score':'ind_score'}
    df_ind.rename(columns=new_name_dict,inplace=True)
    canvas_grades = pd.merge(df_ind,df_group,how='left',left_on='id',
                             right_on='id',sort=False)
    combined_scores=canvas_grades.apply(mark_combined,axis=1)
    canvas_grades['combined'] = combined_scores
    from e340py.get_grade_frames import make_canvas_df
    canvas_path = root_dir / Path(n.grade_book)
    with open(canvas_path,'r',encoding='ISO-8859-1') as f:
        df_canvas=pd.read_csv(f)
    #
    # drop the mute/unmute column
    #
    #df_canvas=df_canvas.drop(df_canvas.index[0])
    points_possible = df_canvas.iloc[0,:5].values
    points_possible[1:5]=[' ',' ',' ',' ']
    df_canvas=clean_id(df_canvas, id_col = 'SIS User ID')
    df_upload=pd.DataFrame(df_canvas.iloc[:,:5])
    df_upload.iloc[1,:]=points_possible
    df_canvas=df_canvas.fillna(0)
    # new_name_dict={'ind_score':'m2_ind_score','group_score':'m2_group_score',
    #                'combined':'m2_combined'}
    # canvas_grades.rename(columns=new_name_dict,inplace=True)
    df_upload = pd.merge(df_upload,canvas_grades,how='left',
                             left_index=True,
                             right_on='id',sort=False)
    del df_upload['id']
    del df_upload['LAST NAME']
    del df_upload['FIRST NAME']
    df_upload.iloc[0,5:]=100
    new_name='mid1_upload.csv'
    with open(new_name,'w',encoding='utf-8-sig') as f:
        df_upload.to_csv(f,index=False,sep=',')
    pdb.set_trace()
    missing_group = canvas_grades['group_score'] < 10.
    canvas_grades.loc[missing_group,'group_score'] = np.nan
    columns=['ind_score',  'group_score','combined']
    fig, ax = plt.subplots(2,2,figsize=(10,10))
    plots=[ax[0,0],ax[0,1],ax[1,0]]
    for column,plot in zip(columns,plots):
        data = canvas_grades[column].values
        data  = data[~np.isnan(data)]
        data_median = np.median(data)
        plot.hist(data)
        plot.set_title(f'{column} median= {data_median}')
    bad=ax[1,1]
    fig.delaxes(bad)
    fig.canvas.draw()
    fig.savefig('grades.png')

    pdb.set_trace()
    print('\ndone\n')

    
if __name__ == "__main__":
    main()

