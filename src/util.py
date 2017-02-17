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

    #writer.writeheader()
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


def process_into_csv_for_grades(directory, out_file, catalog_nbr, subject, year, quarter):
    content_file = directory + '/class_content.json'
    users_file = directory + '/users.json'

    data = open(users_file, 'r')
    parsed = json.load(data)

    for rec in parsed:
        # print rec['name'],
        # print rec['email'],
        # print subject,
        # print catalog_nbr,
        # print quarter,
        # print year,
        # print rec['user_id']
        writer.writerow({'name':str(rec['name'].encode('utf-8').strip()), 'email':rec['email'], 'subject':subject,'catalog_nbr': catalog_nbr, 'quarter':quarter, 'year':year, 'piazza_id':rec['user_id']})


# out_file = '../data/grades_tmp.csv'
# fieldnames = ['name', 'email','subject','catalog_nbr', 'quarter', 'year', 'piazza_id']
# writer = csv.DictWriter(open(out_file,'w'), fieldnames=fieldnames)
# writer.writeheader()

#convertToEdgeList('../data/cs229/fall13')
if __name__ == "__main__":
    DATA_DIRECTORY = '../data/cs231a/'
    for root, dirs, files in os.walk(DATA_DIRECTORY):
        for dir in dirs:
            print dir[len(dir)-2:]
            print dir[:len(dir)-2]
            # print dir[len(dir)-2:],
            # print dir[:len(dir)-2]
            # process_into_csv_for_grades(root+dir, out_file, '229', 'CS', dir[len(dir)-2:], dir[:len(dir)-2])
            #convertToEdgeList(root+dir)

#process_into_csv_for_grades('../data/Fall2012-SOLARONLINE_Solar_Cells_Fuel_Cells_&_Batteries', out_file, '', 'Solar', '2012', 'fall')
#process_into_csv_for_grades('../data/Summer2015-INTWOMENSHEALTH_International_Womens_Health_&_Human_Rights', out_file, '', 'WomensHealth', '2015', 'summer')
#process_into_csv_for_grades('../data/Winter2013-PSYCH_035__SYMSYS_100__LINGUIST_144__PHIL_190_Introduction_to_Cognitive_Science', out_file, '35', 'PSYCH', '2013', 'winter')
