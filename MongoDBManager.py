from pymongo import MongoClient

class MongoDBManager:

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.dq_analyzer_rules_generator
        self.collection = self.db.rules_repository
        self.collection2 = self.db.corrections_repository
        self.collection3 = self.db.data_range_rules

    def insert_doc(self, doc):
        self.collection.insert_one(doc)

    def find_all_docs(self):
        return self.collection.find()

    def find_doc_by_id(self, id):
        return self.collection.find_one({"_id": id})

    def find_doc_by_name(self, name):
        return self.collection.find_one({"name" : name })

    def find_correction_by_name(self, name):
        return self.collection2.find_one({"name": name})

    def find_data_range_rule_by_name(self, name):
        return self.collection3.find_one({"name": name})

