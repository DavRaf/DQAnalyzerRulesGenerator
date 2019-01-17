from MongoDBManager import MongoDBManager
from string import Template
import re
from GeneratedRule import GeneratedRule
from XMLFileManager import XMLFileManager
from DomainAnalysis import DomainAnalysis
from MaskAnalysis import MaskAnalysis
from Pattern import Pattern
import os
import pandas as pd

class RulesManager:

    date_patterns = ('^(N-N-N)$', '^(N.N.N)$', '^(N/N/N/)$')

    def __init__(self):
        self.mongo_db_manager = MongoDBManager()
        self.xml_file_manager = XMLFileManager()
        self.generated_rules = list()
        self.generated_data_range_rules = list()
        self.new_detected_patterns = list()

    def get_rule_by_id(self, id):
        rule = self.mongo_db_manager.find_doc_by_id(id)
        return rule

    def get_all_rules(self):
        rules = self.mongo_db_manager.find_all_docs()
        return rules

    def get_rule_by_name(self, name):
        return self.mongo_db_manager.find_doc_by_name(name)

    def write_rule(self, file, rule_name, rule_expression):
        self.xml_file_manager.write_rule_advanced(file, rule_name, rule_expression)

    def generate_rules(self, profile, plan_file):
        threshold = 70
        rules_expressions_in_plan_file = list()
        for stat in profile.statistics:
            if stat.type == 'count':
                number_of_rows = stat.value
        rule_templates_collection = self.mongo_db_manager.find_all_docs()
        domain_analysis = profile.domain_analysis
        mask_analysis = profile.mask_analysis
        analysis = domain_analysis + mask_analysis
        rules_in_plan_file = self.xml_file_manager.read_rules_from_plan_file(plan_file)
        for rule_plan_file in rules_in_plan_file:
            rules_expressions_in_plan_file.append(rule_plan_file.rule_expression)
        for rule_template in rule_templates_collection:
            for a in analysis:
                if a.value:
                    if re.match(rule_template['pattern'], a.value):
                        if type(a) is DomainAnalysis:
                            domain_percentage = (int(a.num_cases) / int(number_of_rows)) * 100
                            rule = self.process_rule_template(rule_template, profile, a.value, a.num_cases, domain_percentage)
                        elif type(a) is MaskAnalysis:
                            mask_percentage = a.percentage
                            rule = self.process_rule_template(rule_template, profile, a.value, a.count, mask_percentage)
                        if rule:
                            if rule.rule_expression not in rules_expressions_in_plan_file:
                                if rule.pattern_percent:
                                    if rule.pattern_percent >= threshold:
                                        if 'integer' not in profile.domain_name and 'float' not in profile.domain_name:
                                            self.write_rule(plan_file, rule.rule_name, rule.rule_expression)
                            self.generated_rules.append(rule)
                    else:
                        if type(a) is DomainAnalysis:
                            domain_percentage = (int(a.num_cases) / int(number_of_rows)) * 100
                            pattern = Pattern(profile.expression_name, a.value, a.num_cases, domain_percentage)
                        elif type(a) is MaskAnalysis:
                            mask_percentage = a.percentage
                            pattern = Pattern(profile.expression_name, a.value, a.count, mask_percentage)
                        self.new_detected_patterns.append(pattern)
        #self.generated_rules = sorted(list(set(self.generated_rules)), key=lambda x: x.rule_name, reverse=False)
        self.new_detected_patterns = sorted(list(set(self.new_detected_patterns)), key=lambda x: x.column_name, reverse=False)
        for rule in self.generated_rules:
            for pattern in self.new_detected_patterns:
                allowed_chars = set('DLNW./-')
                if pattern.pattern_value == rule.pattern_value or set(pattern.pattern_value).issubset(allowed_chars) is False:
                    self.new_detected_patterns.remove(pattern)

    def generate_range_value_rules(self, plan_file):
        dataset_name = os.path.abspath(self.xml_file_manager.read_dataset_name(plan_file))
        dataset = pd.read_csv(dataset_name, sep=';')  # loads the dataset without considering the headers
        values_list = list()
        n = 0
        for c in dataset:
            cleaned_list = [x for x in dataset[c].values.tolist() if str(x) != 'nan']
            values_list.append(set(cleaned_list))
            rule = GeneratedRule(column_name=c, rule_name="Data Range Rule " + c, rule_expression=c + " in {" + str(values_list[n]).replace("{", "").replace("}", "") + "}")
            self.generated_data_range_rules.append(rule)
            n = n + 1

    def process_rule_template(self, rule_template, profile, pattern_value, pattern_num_cases, pattern_percentage):
        if rule_template['pattern'] in RulesManager.date_patterns and 'day' not in profile.domain_name.casefold():
            return None
        rule_expression_template = Template(rule_template['expression'])
        rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
        return GeneratedRule(profile.expression_name, pattern_value, pattern_num_cases, pattern_percentage, rule_template['name'], rule_template['description'], rule_template['pattern'], rule_expression)


