from MongoDBManager import MongoDBManager
from string import Template
import pprint

class RulesManager:

    def __init__(self):
        self.mongo_db_manager = MongoDBManager()

    def get_rule_by_id_and_replace_value(self, rule_id):
        rule = self.mongo_db_manager.find_doc_by_id(rule_id)
        expression = rule['expression']
        expression = Template(expression)
        expression = expression.safe_substitute(value='src_date')
        print(expression)

    def get_all_rules(self):
        rules = self.mongo_db_manager.find_all_docs()
        for rule in rules:
            pprint.pprint(rule)

    def get_rule_by_name(self, name):
        return self.mongo_db_manager.find_doc_by_name(name)
