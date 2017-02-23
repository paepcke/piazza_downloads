'''
This file executes all functions for processing of courses - cleaning data, inserting into mysql database,
fetching required records, converting them into networks and generating all statisitcs. 

The function main takes 2 arguments, namely 'getStats' (set True if we 
want to calculate the network statistics for all the courses, stored as 'statistics.csv' under each course 
offering in data directory) and 'combine'(set True if we want to compare the stats across various courses
for each network parameter, stored as '{attribute_name}'.csv in data/stats).

All constants are defined in 'constants.py'.
'''

import getpass

import progressbar

from graph import *
from piazza_json_export_to_sql import *
from util import *


def main(getStats = False, combine = False):
    print 'Fetching records from sql..'
    if not os.path.exists('stats'):
        os.makedirs('stats')
    tasks = []
    for c in COURSES:
        for root, dirs, files in os.walk(DATA_DIRECTORY+c+'/'):
            for course_dir in dirs:
                tasks.append({'input':root+course_dir+'/','db_name':c+course_dir})
    bar = progressbar.ProgressBar(maxval=len(tasks), \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    i=0
    for task in tasks:
        bar.update(i+1)
        i+=1
        fetch(task)
    bar.finish()
    print 'Creating Network-----------------------------------------------'
    for course in COURSES:
        print course
        path = DATA_DIRECTORY+course
        
        for root, dirs, files in os.walk(path):
            for course_dir in dirs:
                convertToEdgeList(root+'/'+course_dir,course+course_dir,True)
        
        if getStats: 
            print 'Calculating statistics for',course
            stats(course,True)
    if getStats and combine:
        print 'Combining stats for all courses------------------------------------------'
        combine_statistics()

if __name__ == '__main__':
  pwd = DB_PARAMS.get('password', None)
  if pwd is None:
    DB_PARAMS['password'] = ''
  elif len(DB_PARAMS['password']) == 0:
    DB_PARAMS['password'] = getpass.getpass('MySQL password for user {0}:'.format(DB_PARAMS['user'])) 
  main(True,False)