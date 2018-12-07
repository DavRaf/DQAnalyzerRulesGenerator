from MongoDBManager import MongoDBManager
from string import Template
import re
from Rule import Rule
from XMLFileManager import XMLFileManager

class RulesManager:

    date_patterns = ('^(N-N-N)$', '^(N.N.N)$', '^(N/N/N/)$')

    def __init__(self):
        self.mongo_db_manager = MongoDBManager()
        self.generated_rules = list()

    def get_rule_by_id(self, id):
        rule = self.mongo_db_manager.find_doc_by_id(id)
        return rule

    def get_all_rules(self):
        rules = self.mongo_db_manager.find_all_docs()
        return rules

    def get_rule_by_name(self, name):
        return self.mongo_db_manager.find_doc_by_name(name)

    def write_rule(self, file, rule_name, rule_expression):
        xml_file_manager = XMLFileManager()
        xml_file_manager.write_rule_advanced(file, rule_name, rule_expression)

    def generate_rules(self, profile):
        rule_templates_collection = self.mongo_db_manager.find_all_docs()
        domain_analysis = profile.domain_analysis
        mask_analysis = profile.mask_analysis
        for rule_template in rule_templates_collection:
            if domain_analysis:
                for domain in domain_analysis:
                    if domain.value:
                        if re.match(rule_template['pattern'], domain.value):
                            rule = self.load_rule_template_and_replace_value(rule_template, profile)
                            if rule:
                                self.generated_rules.append(rule)
            if mask_analysis:
                for mask in mask_analysis:
                    if mask.value:
                        if re.match(rule_template['pattern'], mask.value):
                            rule = self.load_rule_template_and_replace_value(rule_template, profile)
                            if rule:
                                self.generated_rules.append(rule)
        self.generated_rules = sorted(list(set(self.generated_rules)), key=lambda x: x.rule_name, reverse=False)

    def load_rule_template_and_replace_value(self, rule_template, profile):
        if rule_template['pattern'] in RulesManager.date_patterns and 'day' not in profile.domain_name.casefold():
            return None
        rule_expression_template = Template(rule_template['expression'])
        rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
        return Rule(rule_template['name'], rule_expression, rule_template['description'])


