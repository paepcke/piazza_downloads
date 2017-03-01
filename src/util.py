import ast
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import operator
import os
import plotly.graph_objs as go
import plotly.plotly as py
import statistics

from constants import *
from datetime import *
from matplotlib import pylab
from numpy import diff
from scipy import interpolate
from scipy import optimize

def print_records(records):
    if records.count()==0: print 'No records found!'

    result = []
    for rec in records:
        result.append((rec['history'][0]['uid'],rec['tags']))
    return result

def get_nodes_and_edges(path):
    weighted_edges = set()
    nodes = set()
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            nodes.add(row[0])
            edge_tuple = (row[0],row[1],int(row[2]))
            if edge_tuple[2]!=0:
                weighted_edges.add(edge_tuple)
    return nodes,weighted_edges

def process_topics(file):
    topics = []
    for line in file:
        topics.append(line.strip().lower())
    return topics

def get_greater_than(fields,values):
    query = '{'
    assert len(fields)==len(values)
    for i in range(len(fields)):
        query+=fields[i]+':{"gt":'+str(values[i])+'},'
    return query+'}'

def write_network_to_file(out_file,user_edges,not_found_file=None,notfound=0):
    fieldnames = ['user1', 'user2','num_interactions']
    writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
    for key in user_edges:
        writer.writerow({'user1': key[0], 'user2': key[1],'num_interactions':user_edges[key]})
    if not_found_file:
        with open(not_found_file,'w') as nf:
             nf.write('\n'.join(str(id) for id in notfound))

'''
Arguments
---------
    - subset: list of students or instructors
    - limit: number of top users we want to retrieve
    - parameters: list of weighted indegree, weighted outdegree, weighted degree, pagerank
                  (each of them is a dictionary with key=student, value=parameter)

Returns
-------
    - dictionaries of each parameter for top {limit} users with their parameter values (key:user,value:parameter value)
'''
def get_best_parameters(subset, limit, parameters):
    in_degree,out_degree,weighted_degree,pagerank = parameters
    best_indeg = dict(sorted({k:in_degree[k] for k in subset if k in in_degree}.iteritems(), key=operator.itemgetter(1), reverse=True)[:limit])
    best_outdeg = dict(sorted({k:out_degree[k] for k in subset if k in out_degree}.iteritems(), key=operator.itemgetter(1), reverse=True)[:limit])
    best_weighteddeg = dict(sorted({k:weighted_degree[k] for k in subset if k in weighted_degree}.iteritems(), key=operator.itemgetter(1), reverse=True)[:limit])
    best_pagerank = dict(sorted({k:pagerank[k] for k in subset if k in pagerank}.iteritems(), key=operator.itemgetter(1), reverse=True)[:limit])
    return best_indeg,best_outdeg,best_weighteddeg,best_pagerank

def find_average(subset,parameters):
    return [
    sum([parameters[0][k] for k in subset[0]])/float(len(subset[0])),
    sum([parameters[1][k] for k in subset[1]])/float(len(subset[1])),
    sum([parameters[2][k] for k in subset[2]])/float(len(subset[2])),
    sum([parameters[3][k] for k in subset[3]])/float(len(subset[3])),
    ]

def find_median(subset,parameters):
    try:
        result=[
            statistics.median([parameters[0][k] for k in subset[0] if parameters[0][k]!=0 ]),
            statistics.median([parameters[1][k] for k in subset[1] if parameters[1][k]!=0 ]),
            statistics.median([parameters[2][k] for k in subset[2] if parameters[2][k]!=0 ]),
            statistics.median([parameters[3][k] for k in subset[3] if parameters[3][k]!=0 ])
        ]
    except:
        result= []

    return result

'''
Separates students from instructors using 'i_answer' and 'i_update' tags from class_content.json.
Assuming that every instructor gives an 'instructor answer' or updates another instructor's answer
at some point in the course.

Arguments
---------
    - course directory
Returns
-------
    - list of instructors
    - list of students
'''
def identify_instructors(directory):
    #print directory
    user_file = directory+'/users.json'
    content_file = directory + '/class_content.json'

    user_data = open(user_file,'r')
    class_data = open(content_file,'r')

    parsed_users = json.load(user_data)
    parsed_class = json.load(class_data)

    instructors = set()
    types = set()
    users = {}

    for rec in parsed_class:
        if 'change_log' in rec:
            for log in rec['change_log']:
                types.add(log['type'])
                if log['type']=='i_answer' or log['type'] == 'i_answer_update':
                    instructors.add(log['uid'])
    for rec in parsed_users:
        users[rec['user_id']] = rec['name']
    # for instructor in instructors:
    #     print users[instructor]
    students = set(users.keys()) - instructors 
    # print '#instructors: ',len(instructors)
    # print '#students: ',len(students)
    return list(instructors), list(students)

'''
This function is used to generate a network from the records fetched from mysql database.
If divide=True, it will also generate a cumulative subnetwork for each week of the course.
The weeks are divided according to the post creation timestamps.

Arguments
----------
   - directory: course directory
   - name:  name of the change_log file created from piazza_json_export_to_sql.py
   - divide: True if we want to divide the network into weekly subnetworks 
Returns
-------
    - None
Output
------
    - directory/network.csv : contains the network
    - directory/not_found.csv : contains list of users present in class_content.json but
                                not in 'users.json' (people who dropped out of the course)
    - directory/subnetwork{i}.csv (if divide=True) : contains the cumulative network uptil week {i}

'''
def convertToEdgeList(directory,name,divide=False):
    user_file = directory+'/users.json'
    children_file = directory+'/'+name+'.txt'
    out_file = directory+'/network.csv'
    not_found_file = directory + '/not_found.txt'

    print children_file

    data = open(user_file, 'r')
    parsed = json.load(data)
    
    user_edges = {}

    # Set of all the users enrolled in the course. Initializing user_edges directory to 0.
    users = set()
    for rec1 in parsed:
        users.add(rec1['user_id'])
        for rec2 in parsed:
            user_edges[(rec1['user_id'],rec2['user_id'])] = 0

    flag=True
    num_week = 1
    d1,d2=0,0
    with open(children_file, 'rb') as f:
      notfound = set()
      for children in f:
        timestamp,children =children.split('\t')[0], ast.literal_eval(children.split('\t')[1])
        if not children: continue

        if not flag:
            d2 = datetime.fromtimestamp(float(timestamp))
        else:
            d1 = datetime.fromtimestamp(float(timestamp))
            d2 = datetime.fromtimestamp(float(timestamp))
            flag = False

        children = [x for x in children if x is not None]
        thread_starter = children[0]

        if thread_starter not in users:
            continue

        for i in range(1,len(children)):
            if children[i] not in users:
                continue
            user_edges[(children[i],thread_starter)]+=1

        # writes another subnetwork as soon as the difference in timestamps becomes greater than 7
        if divide and (d2-d1).days/7>=1:    
            #print 'Week: ',num_week, ' Dates: ', d1, ' To: ', d2        
            write_network_to_file(directory+'/subnetwork'+str(num_week)+'.csv',user_edges,None,0)
            flag=True
            num_week+=1 
    # writes the final network file  
    print out_file
    write_network_to_file(out_file,user_edges,not_found_file,notfound)

def process_into_csv_for_grades(directory, out_file, catalog_nbr, subject, year, quarter):
    content_file = directory + '/class_content.json'
    users_file = directory + '/users.json'

    data = open(users_file, 'r')
    parsed = json.load(data)

    for rec in parsed:
        writer.writerow({'name':str(rec['name'].encode('utf-8').strip()), 'email':rec['email'], 'subject':subject,'catalog_nbr': catalog_nbr, 'quarter':quarter, 'year':year, 'piazza_id':rec['user_id']})

'''
This function takes in individual network statistics from all courses and combines them
by creating a csv file for each network attribute. The statistics files are stored in
piazza/data/stats

Arguments
----------
    - None
Returns
-------
    - None
Output
------
    - piazza/data/stats/{attribute}.csv
'''
def combine_statistics():
    attributes = ['Nodes', 'Edges','Avg In Degree','Avg Out Degree','Avg Degree','Avg Weighted Degree', 'Density', 'Largest Strongly Connected Component','Largest Weakly Connected Component', 'Average Betweenness Centrality', 'Average Closeness Centrality', 'Average Degree Centrality', 'Average Eigenvector Centrality', 'Average Clustering Coefficient', 'Average Hub Score', 'Average Authority Score', 'Max Pagerank']

    for att in attributes:
        print att+'||',
        out_file = open(DATA_DIRECTORY+'stats/'+att+'.stats.csv','wb')
        writer = csv.writer(out_file)
        writer.writerow(['']+COURSES)

        dictnodes = {'FALL11':[],'FALL12':[],'SUMMER13':[],'FALL13':[],'WINTER14':[],'SPRING14':[],'FALL14':[],'WINTER15':[],'FALL15':[],'SPRING16':[],'FALL16':[]}

        counter = 0
        for course in COURSES:
                counter+=1
                path = DATA_DIRECTORY+course
                f_stats = open(path+'/statistics.csv','r')
                reader = csv.DictReader(f_stats)
                for row in reader:
                    dictnodes[row['Course']].append(row[att])
                for key in dictnodes:
                   if len(dictnodes[key])<counter: dictnodes[key].append(0)
        for key in dictnodes:
            writer.writerow([key]+dictnodes[key])

def critical_points(x,y):
    derivative =  diff(np.array(y))

    critical_points = []
    zero_crossings = np.where(np.diff(np.sign(derivative)))[0]
    zero_crossings = [i+1 for i in zero_crossings]
    prev = 0
    resultx = []
    resulty = []
    addlistx = []
    addlisty = []
    for elem in zero_crossings:
        addlistx = []
        addlisty = []
        if elem-prev==1:
            if x[prev] not in addlistx: 
                addlistx.append(x[prev])
                addlisty.append(y[prev])
            addlistx.append(x[elem])
            addlisty.append(y[elem])
        else:
            addlistx.extend(x[prev:elem])
            addlisty.extend(y[prev:elem])
        resultx.append(addlistx)
        resulty.append(addlisty)
        prev=elem
    if addlistx:
        resultx.append(addlistx)
        resulty.append(addlisty)

    resultx.append(x[prev:]) 
    resulty.append(y[prev:]) 
    return resultx,resulty


def spline_interpolation(x,y1,y2,plot_name,plot_title,out_directory,xlabel,ylabel):
    x = np.array(x)
    y1 = np.array(y1)
    tck = interpolate.splrep(x, y1, k=2, s=0)
    xnew = np.linspace(0, 15)

    fig, axes = plt.subplots(3)

    # box = axes[2].get_position()
    # axes[2].set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    axes[0].plot(x, y1, 'o',color='r', markersize=10, label = 'avg trend for top 10% students')
    axes[0].plot(x,y2,'-',color='g',label='median of rest of the students')

    dev_1 = interpolate.splev(x, tck, der=1)
    axes[2].plot(x, dev_1, label = '1st derivative')

    turning_point_mask = dev_1 == np.amax(dev_1)

    axes[2].plot(x[turning_point_mask], dev_1[turning_point_mask],'rx',mew=7, color='r', markersize=15,
                 label = 'Inflection point')
    
    x_divisions,y_divisions = critical_points(x,y1)
    colors = ['m','k','y']
    for i in range(len(x_divisions)):
            fit = np.polyfit(x_divisions[i],y_divisions[i],1)
            fit_fn = np.poly1d(fit) 
            axes[1].plot(x_divisions[i],fit_fn(x_divisions[i]),'-',color=colors[i%len(colors)])

    axes[1].plot(x, y1, 'o',color='b', markersize=6)

    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[2].get_legend_handles_labels()
    axes[2].set_xlabel(xlabel)
    axes[1].set_ylabel(ylabel)

    # Put a legend below current axis
    axes[2].legend(h1+h2,l1+l2,loc='upper center', bbox_to_anchor=(0.5, -0.09),
              fancybox=True, shadow=True, ncol=2,fontsize=8)

    # Saving the plot to piazza/figures
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    plt.savefig(out_directory +plot_name)
    #plt.show()
'''
Plots parameter trends (1st degree polynomial fit) for top 10% students in the course
This function goes over all the directories to plot the parameter with respect to weeks
in the course. It adds a line to the same figure for every course offering.

Arguments
---------
    - directory: course directory
    - parameter: 'Degree'/'Pagerank'
    - ax: pyplot axis

Returns:
--------
    - None

Output
------
    plots in piazza/figures
'''
def plot_weekly_change_in_parameter(directory, parameter,ax):
    weeks = 1
    y1 = []
    y2 = []

    top_student_statistics = directory + '/top_statistics_student.csv'
    median_student_statistics = directory + '/median_statistics_student.csv'

    f_top_students = open(top_student_statistics,'r')
    f_median_students = open(median_student_statistics,'r')

    reader1 = csv.reader(f_top_students)
    reader2 = csv.reader(f_median_students)

    # Skipping the header of the csv file
    next(reader1, None)
    next(reader2,None)
    data = list(reader1)

    # Returning if csv is empty
    if len(data)<3: 
        return
    
    for row in data:
        _,_,deg,_,pagerank = row
        if parameter=='Weighted Out Degree': 
            y1.append(float(deg))
        elif parameter=='Pagerank':
            y1.append(float(pagerank))
        weeks+=1
    weeks = range(1,weeks)

    for row in reader2:
        _,_,deg,_,pagerank = row
        if parameter=='Weighted Out Degree': 
            y2.append(float(deg))
        elif parameter=='Pagerank':
            y2.append(float(pagerank))


    plot_title = str(directory.split('/')[2])+str(directory.split('/')[3])+' '+ parameter+'\n Comparison between best-value trend and median for students in the course'
    print str(directory.split('/')[2])+' Comparison for '+parameter
    out_directory = '../figures/'+str(directory.split('/')[2])
    plot_name = '/'+'comparison_'+parameter+'_'+str(directory.split('/')[3])+'.png'
    spline_interpolation(weeks,y1,y2,plot_name,plot_title,out_directory,'Week',parameter)

if __name__ == "__main__":
    for course in COURSES:
            print course    
            for root, dirs, files in os.walk('../stats/'+course+'/'):
                for dir in dirs:
                    print root+dir
                    plot_weekly_change_in_parameter(root+dir,'Pagerank',None)
                    plot_weekly_change_in_parameter(root+dir,'Weighted Out Degree',None)
