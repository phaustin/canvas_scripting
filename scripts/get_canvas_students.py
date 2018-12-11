import context
import pdb
import pandas as pd

from e340py.utils import login_courses, start_logging
def get_students(course_name):
    canvas, keep = login_courses()
    course=canvas.get_course(keep[course_name])
    out = course.get_enrollments()
    all_students=[item for item in out]
    name_id_canid=[(item.user['sortable_name'], item.user['sis_user_id'], item.user['id']) for item in all_students]
    df=pd.DataFrame.from_records(name_id_canid,columns=['name','id','canid'])
    return course,df

if __name__ == "__main__":
    course,df=get_students('e340')
    assignments=course.get_assignments()
    good_list=[item for item in assignments if item.published]
    assign_names=[(item.name,item.attributes['id'],item.attributes['due_at']) for item in good_list]
    submits=good_list[20].get_submissions()
    all_submits=[item for item in submits]
    out = good_list[20].get_submission(user=11732,include=['submission_history'])
    print(out.__dict__['submission_history'][0]['submission_data'])
    pdb.set_trace()
    
