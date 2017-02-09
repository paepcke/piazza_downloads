import json
import csv
import ast
import os

def print_records(records):
    if records.count()==0: print 'No records found!'

    result = []
    for rec in records:
        result.append((rec['history'][0]['uid'],rec['tags']))
    return result

def get_greater_than(fields,values):
    query = '{'

    assert len(fields)==len(values)

    for i in range(len(fields)):
        query+=fields[i]+':{"gt":'+str(values[i])+'},'
    return query+'}'

def convertToEdgeList(directory):
    print directory
    user_file = directory+'/users.json'
    children_file = directory+'/interactions.txt'
    out_file = directory+'/result.csv'
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
      #reader = csv.DictReader(csvfile, delimiter='\t', quotechar='|')
      notfound = set()
      for children in f:
        children = ast.literal_eval(children)
        children = [x for x in children if x is not None]
        #print children
        
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

    writer.writeheader()
    for key in user_edges:
        writer.writerow({'user1': key[0], 'user2': key[1],'num_interactions':user_edges[key]})
    with open(not_found_file,'w') as nf:
         nf.write('\n'.join(str(id) for id in notfound))
    #print notfound
    #print user_edges.values()
    #print user_edges[("i0efktx1sdw4oj","i0efktx1sdw4oj")]
    print '# edges: ',sum(user_edges.values())
    print '# users: ', len(users)
    print '# not found:',len(notfound)

DATA_DIRECTORY = '../data/cs229/'
for root, dirs, files in os.walk(DATA_DIRECTORY):
    for dir in dirs:
        convertToEdgeList(root+dir)


