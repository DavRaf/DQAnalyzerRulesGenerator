from pymongo import MongoClient

class MongoDBManager:

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.dq_analyzer_rules_generator
        self.collection = self.db.rules_repository

    def insert_doc(self, doc):
        self.collection.insert_one(doc)

    def find_all_docs(self):
        '''for doc in self.collection.find():
            pprint.pprint(doc)'''
        return self.collection.find()

    def find_doc_by_id(self, id):
        #pprint.pprint(self.collection.find_one({"_id": id}))
        return self.collection.find_one({"_id": id})

    def find_doc_by_name(self, name):
        return self.collection.find_one({"name" : name })

    '''def upsert_doc(self, doc):
        self.collection.update(doc)'''