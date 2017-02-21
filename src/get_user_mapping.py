import os
import json
from pprint import pprint
import csv
import io

'''
This file takes in the course directory and parses the 'users.json' in each course offering into 'user_mapping.csv' to 
create a mapping of all piazza user_ids with their names and email_ids.
'''

DATA_DIRECTORY = '../data/'

def create(subdir,filepath):
    csvfile = open(subdir+'/users_mapping.csv','w')
    writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    with open(filepath,'r') as f_in:
        data = json.load(f_in)
        fieldnames = ['piazza_id', 'name','email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in data:
          user_id =  key['user_id']
          name = key['name']
          email = key['email']
          print user_id,name,email
          writer.writerow({'piazza_id':str(user_id),'name':str(name.encode('utf-8').strip()), 'email':str(email)})


def main():
    for subdir, dirs, files in os.walk(DATA_DIRECTORY):
        for class_file in files:
            filepath = subdir + os.sep + class_file

            if class_file=='users.json':
                print (filepath)
                create(subdir,filepath)
main()