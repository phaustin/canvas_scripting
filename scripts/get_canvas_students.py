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
    return df

if __name__ == "__main__":
    df=get_students('e340')
    pdb.set_trace()
    
