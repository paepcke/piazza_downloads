import json
import csv
import ast
import os
from constants import *

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

def convertToEdgeList(directory,name):
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
    with open(children_file, 'rb') as f:
      notfound = set()
      for children in f:
        children = ast.literal_eval(children.split('\t')[1])
        children = [x for x in children if x is not None]
        
        for i in range(len(children)):
                for j in range(i,len(children)):
                        if children[i] not in users:
                            notfound.add(children[i])
                            continue
                        if children[j] not in users:
                            notfound.add(children[j])
                            continue
                        user_edges[(children[j],children[i])]+=1
    fieldnames = ['user1', 'user2','num_interactions']
    writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
    for key in user_edges:
        writer.writerow({'user1': key[0], 'user2': key[1],'num_interactions':user_edges[key]})
    with open(not_found_file,'w') as nf:
         nf.write('\n'.join(str(id) for id in notfound))
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
