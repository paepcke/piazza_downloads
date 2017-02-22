import json
import csv
import ast
import os
import operator
import numpy as np
from constants import *
from datetime import *
import matplotlib.pyplot as plt
from matplotlib import pylab
import plotly.plotly as py
import plotly.graph_objs as go

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
            #print row
            nodes.add(row[0])
            edge_tuple = (row[0],row[1],int(row[2]))
            if edge_tuple[2]!=0:
                weighted_edges.add(edge_tuple)
    return nodes,weighted_edges
def get_greater_than(fields,values):
    query = '{'
    assert len(fields)==len(values)
    for i in range(len(fields)):
        query+=fields[i]+':{"gt":'+str(values[i])+'},'
    return query+'}'

def write_network_to_file(out_file,not_found_file,notfound,user_edges):
    fieldnames = ['user1', 'user2','num_interactions']
    writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
    for key in user_edges:
        writer.writerow({'user1': key[0], 'user2': key[1],'num_interactions':user_edges[key]})
    with open(not_found_file,'w') as nf:
         nf.write('\n'.join(str(id) for id in notfound))


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

def convertToEdgeList(directory,name,divide=False):
    user_file = directory+'/users.json'
    children_file = directory+'/'+name+'.txt'
    out_file = directory+'/network.csv'
    not_found_file = directory + '/not_found.txt'

    data = open(user_file, 'r')
    parsed = json.load(data)
    
    user_edges = {}
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

        if not flag:
            d2 = datetime.fromtimestamp(float(timestamp))
        else:
            d1 = datetime.fromtimestamp(float(timestamp))
            d2 = datetime.fromtimestamp(float(timestamp))
            flag = False

        children = [x for x in children if x is not None]
        thread_starter = children[0]

        if thread_starter not in users:
            notfound.add(thread_starter)
            continue

        for i in range(1,len(children)):
            if children[i] not in users:
                continue
            user_edges[(children[i],thread_starter)]+=1
        if divide and (d2-d1).days/7>=1:            
            write_network_to_file(directory+'/subnetwork'+str(num_week)+'.csv',directory + '/sub_not_found'+str(num_week)+'.txt',notfound,user_edges)
            flag=True
            num_week+=1   
    write_network_to_file(out_file,not_found_file,notfound,user_edges)

    # print '# edges: ',sum(user_edges.values())
    # print '# users: ', len(users)
    # print '# not found:',len(notfound)


def process_into_csv_for_grades(directory, out_file, catalog_nbr, subject, year, quarter):
    content_file = directory + '/class_content.json'
    users_file = directory + '/users.json'

    data = open(users_file, 'r')
    parsed = json.load(data)

    for rec in parsed:
        writer.writerow({'name':str(rec['name'].encode('utf-8').strip()), 'email':rec['email'], 'subject':subject,'catalog_nbr': catalog_nbr, 'quarter':quarter, 'year':year, 'piazza_id':rec['user_id']})


def combine_statistics():
    attributes = ['Nodes', 'Edges','Avg In Degree','Avg Out Degree','Avg Degree','Avg Weighted Degree', 'Density', 'Largest Strongly Connected Component','Largest Weakly Connected Component', 'Average Betweenness Centrality', 'Average Closeness Centrality', 'Average Degree Centrality', 'Average Eigenvector Centrality', 'Average Clustering Coefficient', 'Average Hub Score', 'Average Authority Score', 'Max Pagerank']

    for att in attributes:
        print att+'||',
        out_file = open(DATA_DIRECTORY+'stats/'+att+'.stats.csv','wb')
        writer = csv.writer(out_file)
        writer.writerow(['']+COURSES)

        dictnodes = {'FALL11':[],'FALL12':[],'SUMMER13':[],'FALL13':[],'WINTER14':[],'SPRING14':[],'FALL14':[],'WINTER15':[],'FALL15':[],'SPRING16':[],'FALL16':[]}

        #COURSES = ['cs229']
        counter = 0
        for course in COURSES:
                counter+=1
                path = DATA_DIRECTORY+course
                #print course
                f_stats = open(path+'/statistics.csv','r')
                reader = csv.DictReader(f_stats)
                for row in reader:
                    dictnodes[row['Course']].append(row[att])
                for key in dictnodes:
                   if len(dictnodes[key])<counter: dictnodes[key].append(0)
        for key in dictnodes:
            writer.writerow([key]+dictnodes[key])


def plot_weekly_change_in_parameter(directory, parameter,ax):
    student_statistics = directory + '/statistics_student.csv'

    f_student = open(student_statistics,'r')
    reader = csv.reader(f_student)
    next(reader, None)
    weeks = 1
    x = []
    data = list(reader)
    if len(data)<3: 
        return
    for row in data:
        _,_,_,deg,pagerank = row

        if parameter=='Degree': 
            x.append(float(deg))
        elif parameter=='Pagerank':
            x.append(float(pagerank))
        weeks+=1
    weeks = range(1,weeks)
    # print 'X: ',weeks
    # print 'Y: ',pageranks
    z = np.polyfit(weeks,x,3)
    f = np.poly1d(z)
    y_new = f(weeks)
    #plt.clf()

    ax.plot(weeks,x,'o')
    ax.plot(weeks,y_new,label=str(directory.split('/')[3]))
    pylab.title(str(directory.split('/')[2])+' Polynomial Fit for '+parameter)
    plt.xlabel('Week #')
    plt.ylabel(parameter)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=13)
    # ax = plt.gca()
    # ax.set_axis_bgcolor((0.898, 0.898, 0.898))
    # fig = plt.gcf()
    print str(directory.split('/')[2])+' Polynomial Fit for '+parameter

    out_directory = '../figures/'+str(directory.split('/')[2])
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    plt.savefig('../figures/'+str(directory.split('/')[2])+'/'+'polyfit_'+parameter+'_'+str(directory.split('/')[3])+'.png')
    #py.plot_mpl(fig, filename=directory)
    #plt.show()


if __name__ == "__main__":
    for course in COURSES:
            print course
            fig = plt.figure()
            ax = plt.subplot(111)
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            
            for root, dirs, files in os.walk(DATA_DIRECTORY+course+'/'):
                for dir in dirs:
                    print root+dir
                    plot_weekly_change_in_parameter(root+dir,'Pagerank',ax)
