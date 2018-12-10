from MongoDBManager import MongoDBManager
from string import Template
import re
from GeneratedRule import GeneratedRule
from XMLFileManager import XMLFileManager
from DomainAnalyse import DomainAnalyse
from MaskAnalysis import MaskAnalysis

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

    def generate_rules(self, profile, plan_file):
        threshold = 70
        for stat in profile.statistics:
            if stat.type == 'count':
                number_of_rows = stat.value
        rule_templates_collection = self.mongo_db_manager.find_all_docs()
        domain_analysis = profile.domain_analysis
        mask_analysis = profile.mask_analysis
        analysis = domain_analysis + mask_analysis
        for rule_template in rule_templates_collection:
            for a in analysis:
                if a.value:
                    if re.match(rule_template['pattern'], a.value):
                        if type(a) is DomainAnalyse:
                            domain_percentage = (int(a.num_cases) / int(number_of_rows)) * 100
                            rule = self.process_rule_template(rule_template, profile, a.value, a.num_cases, domain_percentage)
                        elif type(a) is MaskAnalysis:
                            mask_percentage = a.percentage
                            rule = self.process_rule_template(rule_template, profile, a.value, a.count, mask_percentage)
                        if rule:
                            if rule.pattern_percent >= threshold:
                                self.write_rule(plan_file, rule.rule_name, rule.rule_expression)
                            self.generated_rules.append(rule)
        self.generated_rules = sorted(list(set(self.generated_rules)), key=lambda x: x.rule_name, reverse=False)

    def process_rule_template(self, rule_template, profile, pattern_value, pattern_num_cases, pattern_percentage):
        if rule_template['pattern'] in RulesManager.date_patterns and 'day' not in profile.domain_name.casefold():
            return None
        rule_expression_template = Template(rule_template['expression'])
        rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
        return GeneratedRule(profile.expression_name, pattern_value, pattern_num_cases, pattern_percentage, rule_template['name'], rule_template['description'], rule_template['pattern'], rule_expression)


