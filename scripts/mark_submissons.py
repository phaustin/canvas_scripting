"""
* mark submissions

https://github.com/ucfopen/canvasapi/issues/147
"""
## Pick course, assignment, student, and set new grade
course = canvas.get_course( -- course number --- )
a = course.get_assignment( -- assignment id --)
x = -- student ID  --
new_grade = 10

## Modify assignment grade for one student 
print (a.name, '--', a.created_at[:10], a.due_at[:10], a.updated_at)
s1 = b.get_submission(x)
print(x, s1.id, 'Current grade:', s1.grade)
s1.edit(submission={'posted_grade': new_grade})

##Check result
s2 = b.get_submission(x)
print(x, s2.id, 'Modified:', s2.grade)
