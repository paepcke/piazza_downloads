from util import *
from piazza_json_export_to_sql import *
from graph import *
import progressbar

'''
This file executed all functions for processing of courses - cleaning data, inserting into mysql database,
fetching required records and converting them into a network (under 'network.csv' in each course for all their
respective offerings in data directory). The function main takes 2 arguments, namely 'getStats' (set True if we 
want to calculate the network statistics for all the courses, stored as 'statistics.csv' under each course 
offering in data directory) and 'combine'(set True if we want to compare the stats across various courses
for each network parameter, stored as '{attribute_name}'.csv in data/stats).

All constants are defined in 'constants.py'.
'''

def main(getStats = False, combine = False):
    print 'Fetching records from sql..'
    tasks = []
    for c in COURSES:
        for root, dirs, files in os.walk(DATA_DIRECTORY+c+'/'):
            for dir in dirs:
                tasks.append({'input':root+dir+'/','db_name':c+dir})
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
            for dir in dirs:
                convertToEdgeList(root+'/'+dir,course+dir,True)
        if getStats: 
            print 'Calculating statistics for',course
            stats(course,True)
    if getStats and combine:
        print 'Combining stats for all courses------------------------------------------'
        combine_statistics()

main(True,False)