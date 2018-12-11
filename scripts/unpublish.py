import json
import pdb

filename='e340_course.json'

with open('e340_course.json','r') as f:
    course_dict=json.load(f)
    
print(f'module count: {len(list(course_dict.keys()))}')

item_count=0
for key,value in course_dict.items():
    print(f"{value['name']} -- {len(value['items'])}")
    item_count += len(value['items'])
    
print(f'item count: {item_count}')
