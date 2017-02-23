'''
Takes paths containing users.json and class_content.json for class exports, and generates corresponding MySQL databases containing forum post data.
Note that not all post metadata is created in the databases. However, the essential requirements for analytics (who posted what when, which tags, ... etc) are taken care of.

For each class, a database with two tables is created:
1- 'users' table
2- 'class_content' table: containing forum post metadata. A special 'is_root' column has been added. This is to help conveniently index root posts (that is, posts that are not answers, ... etc to other posts).

Please edit 'tasks' and 'DB_PARAMS' below.
Tasks is a list where each item is a dict with two keys: input, and db_name
'input' must be a path to a folder containing users.json and class_content.json files for a class.
'db_name' is the name of the database to which the data will be loaded.
'''

import json, time
import os
import shutil
import tempfile

from datetime import datetime

import MySQLdb as mdb

from constants import *


def fetch(task):
    #print task['db_name']
    # Connect to the database using the specified parameters
    con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
    cur = con.cursor(mdb.cursors.DictCursor)

    # Create the database. Overwrites any existing instance.
    q = "DROP DATABASE IF EXISTS {0};".format(task['db_name'])
    try:
        cur.execute(q)
    except:
        pass
    
    q = "CREATE DATABASE {0};".format(task['db_name'])
    cur.execute(q)

    q = "USE {0};".format(task['db_name'])
    cur.execute(q)

    ## Create the users table
    ##########################

    q = "CREATE TABLE users (id varchar(255) PRIMARY KEY, answers int, asks int, posts int, views int, days int);"
    cur.execute(q)

    f = open(task['input'] + 'users.json', 'rb')
    data = json.loads(f.read())
    f.close()

    for x in data:
        q = "INSERT INTO users (id, answers, asks, posts, views, days) VALUES ('{0}',{1},{2},{3},{4},{5});".format(x['user_id'], x['answers'], x['asks'], x['posts'], x['views'], x['days'])
        cur.execute(q)

    ## Create the class content table
    ##################################

    q = "CREATE TABLE class_content (id varchar(255) PRIMARY KEY, type varchar(255), created BIGINT, user_id varchar(255), anon varchar(255), subject LONGTEXT, content LONGTEXT, status varchar(255), nr int, no_answer_followup int, tags LONGTEXT, children LONGTEXT, is_root int, change_log LONGTEXT);"
    cur.execute(q)

    f = open(task['input'] + 'class_content.json', 'rb')
    data = json.loads(f.read())
    f.close()

    def parse_posts(x):
                if 'created' in x.keys():
                    tc = x['created']
                else: tc = '2000-01-10T00:00:00Z'
                dt = datetime(int(tc[0:4]), int(tc[5:7]), int(tc[8:10]), int(tc[11:13]), int(tc[14:16]), int(tc[17:19]))
                
                # if 'history' not in x.keys():
                #     print ""
                #     for k in sorted(x.keys()): print k, ":", x[k]

                nodes = []
                if 'history' in x.keys():
                    nodes .append({
                        'id': x['id'],
                        'type': x['type'],
                        'created': time.mktime(dt.timetuple()),
                        'user_id': x['history'][0]['uid'] if 'uid' in x['history'][0].keys() else 'None',
                        'anon': x['history'][0]['anon'],
                        'subject': x['history'][0]['subject'],
                        'content': x['history'][0]['content'],
                        'status': x['status'] if 'status' in x.keys() else 'None',
                        'nr': x['nr'],
                        'no_answer_followup': x['no_answer_followup'],
                        'tags': json.dumps(x['tags']),
                        'children': json.dumps([c['uid'] if 'uid' in c.keys() else 'None' for c in x['children'] ]),
                        'is_root': 1,
                        'changelog': json.dumps([c['uid'] if 'uid' in c.keys() else 'None' for c in x['change_log']])
                    })

                # if 'children' in x.keys():
                #     for c in x['children']:
                #         nodes.extend(ChildTreeToList(c))
                return nodes

    for x in data:
        nodes = parse_posts(x)

        for node in nodes:
            #print 'NODE:',node
            q = "INSERT INTO class_content VALUES ('{0}','{1}', {2}, {3}, '{4}', '{5}', '{6}', '{7}', {8},{9},'{10}','{11}', {12}, '{13}');".format(
                node['id'],
                node['type'],
                node['created'],
                'null' if not node['user_id'] else "'"+node['user_id']+"'",
                node['anon'],
                node['subject'].replace("\\", "%").replace("'", "\\'").encode('utf-8'),
                node['content'].replace("\\", "%").replace("'", "\\'").encode('utf-8'),
                node['status'],
                node['nr'],
                node['no_answer_followup'],
                node['tags'],
                node['children'],
                node['is_root'],
                node['changelog']
            )
            #print q
            cur.execute(q)
    filename = os.getcwd()[:-3]+task['input'][3:]+task['db_name']+'.txt'
    mysql_out_file_obj = tempfile.NamedTemporaryFile(dir='/tmp', prefix=task['db_name'])
    # Close the file to make it not exist, but
    # use its unique name below. Not good practice
    # because there could be race conditions with
    # other programs asking for a temp file and
    # getting the exact one before MySQL can write
    # to it. But in our situation it's OK:
    mysql_out_file_obj.close()
    #print filename
    try:
        os.remove(filename)
    except OSError:
        pass
    cur.execute("select created,change_log from class_content LIMIT 5,18446744073709551615 INTO OUTFILE '{0}'".format(mysql_out_file_obj.name))
    #cur.execute("select created,change_log from class_content LIMIT 5,18446744073709551615 INTO OUTFILE '{0}'".format(filename))
    #cur.execute("select created,change_log from class_content INTO OUTFILE '/usr/local/dbout/{0}.txt'".format(task['db_name']))
    con.commit()
    con.close()
    shutil.copyfile(mysql_out_file_obj.name, filename)

def ChildTreeToList(x):
    tc = x['created']
    dt = datetime(int(tc[0:4]), int(tc[5:7]), int(tc[8:10]), int(tc[11:13]), int(tc[14:16]), int(tc[17:19]))
    if 'uid' not in x.keys():
        x['uid'] = 'None'

    child_list = []

    if 'anon' in x.keys():
        #print x['children']
        child_list.append({
            'id': x['id'],
            'type': x['type'],
            'created': time.mktime(dt.timetuple()),
            'user_id': x['uid'],
            'anon': x['anon'],
            'subject': '',
            'content': x['subject'],
            'status': '',
            'nr': 0,
            'no_answer_followup': 0,
            'tags': json.dumps([]),
            'children': json.dumps([c['uid'] if 'uid' in c.keys() else 'None' for c in x['children'] ]),
            'is_root': 0,
            'changelog':'None'
        })

    for c in x['children']:
        child_list.extend(ChildTreeToList(c))
    return child_list
