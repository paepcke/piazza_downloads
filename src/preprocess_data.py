#!/usr/bin/python
import pymongo
import json
from util import *

class MongoDbConnection:
    #table = None
    def __init__(self):
        # Connection to Mongo DB
        try:
            conn=pymongo.MongoClient()
            print "Connected to MongoDb successfully"
        except pymongo.errors.ConnectionFailure, e:
                print "Could not connect to MongoDB: %s" % e

        # creates database named content
        self.db = conn.content
        # creates table users in database
        self.table = self.db.users
        # drops any previous data it may contain
        self.table.drop()
    
    # Inserts all data from JSON file into mongodb
    def insert_data(self,json_filepath):
        # loads json file and inserts into our table
        data = open(json_filepath, 'r')
        #page = open("../data/cs229/fall11/class_content.json", 'r')
        parsed = json.loads(data.read())
        for item in parsed:
            self.table.insert_one(item)
        print 'Inserted data successfully'
    
    # Retrieves all records in the table
    def get_all_records(self):
        print_records(self.table.find())
    
    # Returns number of records in table
    def get_record_count(self):
        return self.table.find().count()
    
    # Returns records with field set to specific value
    # display: fields that we want to show
    def get_records_with_field(self, field, value, display=None):
        print_records(self.table.find({field:value},display))
    
    # Returns records with field value greater than given value
    def get_records_greater_than(self, field, value, display=None):
        print_records(self.table.find({field:{"$gt":value}},display))

    # Returns records with field value less than given value
    def get_records_less_than(self, field, value, display=None):
        print_records(self.table.find({field:{"$lt":value}},display))
    
    # Sort records in ascending/descending order
    def sort_records(self,field,ASCENDING=True, display=None):
        if ASCENDING: print_records(self.table.find({},display).sort([(field,pymongo.ASCENDING)]))
        else: print_records(self.table.find({},display).sort([(field,pymongo.DESCENDING)]))
    
    # Returns unique values of field
    def get_distinct(self,field,display=None):
        return self.table.find({},display).distinct(field)

    # many_and = self.table.find({"nr":{"$gt":10},"no_answer":{"$gt":9}})
    # many_or = self.table.find(
    #     {"$or":[
    #     {"asks":{"$gt":20}},
    #     {"answers":{"$gt":20}}
    #     ]})


if __name__ == "__main__":
    mongoCon = MongoDbConnection()
    mongoCon.insert_data("../data/cs229/fall11/class_content.json")
    # mongoCon.get_all_records()
    mongoCon.get_records_with_field("children.tag_endorse.role","ta",{"children.tag_endorse.role":1,"children.tag_endorse.name":1,"_id":0})
    # mongoCon.get_records_greater_than("nr",600)
    # mongoCon.sort_records("nr",False,{"nr":1,"_id":0})
    #print mongoCon.get_distinct("type")