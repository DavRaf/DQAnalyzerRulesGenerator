from MongoDBManager import MongoDBManager
from string import Template
import re

from XMLFileManager import XMLFileManager


class RulesManager:

    #date_patterns = ('N-N-N', 'N/N/N', 'N.N.N')
    ssn_or_sin_masks = ('DDDDDDDDD', 'DDD-DD-DDDD', 'DDD-DDD-DDD', 'DDD DD DDDD', 'DDD DDD DDD', 'LLLDDDDDDDDD', 'LLL:DDDDDDDDD', 'LLL:DDD-DD-DDDD', 'LLL:DDD-DDD-DDD', '9', '9 9 9', '9-9-9', 'SIN: 9')
    fiscal_code_masks = ('LLLLLLDDLDDLDDDL','LL:LLLLLLDDLDDLDDDL')
    ipv4_patterns = ('N.N.N.N','D.D.D.D','N.D.D.D','N.N.D.D','N.N.N.D','D.N.N.N','D.D.N.N','D.D.D.N','N.D.N.D','D.N.D.N','N.D.D.N','D.N.N.D')

    def __init__(self):
        self.mongo_db_manager = MongoDBManager()

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

    def generate_date_rules(self, profile, plan_file):
        if 'string' in profile.expression_type.casefold() and 'day' in profile.domain_name.casefold():
            pattern = profile.get_pattern()
            if pattern:
                if pattern == 'N-N-N':
                    self.load_rule_template_and_replace_value("US Date format YYYY-mm-DD", profile, plan_file)
                    self.load_rule_template_and_replace_value("EU Date format DD-mm-YYYY", profile, plan_file)
                elif pattern == 'N/N/N':
                    self.load_rule_template_and_replace_value("US Date format YYYY/mm/DD", profile, plan_file)
                    self.load_rule_template_and_replace_value("EU Date format DD/mm/YYYY", profile, plan_file)
                elif pattern == 'N.N.N':
                    self.load_rule_template_and_replace_value("US Date format YYYY.mm.DD", profile, plan_file)
                    self.load_rule_template_and_replace_value("EU Date format DD.mm.YYYY", profile, plan_file)

    def generate_ssn_rules(self, profile, plan_file):
        mask = profile.get_mask()
        if mask:
            if len(mask) == 9 or mask in RulesManager.ssn_or_sin_masks:
                    self.load_rule_template_and_replace_value("SSN", profile, plan_file)

    def generate_fiscal_code_rules(self, profile, plan_file):
        mask = profile.get_mask()
        if mask:
            if len(mask) == 16:
                if mask in RulesManager.fiscal_code_masks:
                    self.load_rule_template_and_replace_value("Fiscal Code", profile, plan_file)

    def generate_len_number_rules(self, profile, plan_file):
        if 'integer' not in profile.domain_name:
            pattern = profile.get_pattern()
            mask = profile.get_mask()
            if pattern and mask:
                if pattern == 'N' or pattern == 'W':
                    self.load_rule_template_and_replace_value("Field length", profile, plan_file)

    def generate_email_rules(self, profile, plan_file):
        mask = profile.get_mask()
        if mask:
            if re.match("([W._-]+@[W._-]+\.[W]+)", mask):
                self.load_rule_template_and_replace_value("Email tester 1", profile, plan_file)
            elif re.match("<([W._-]+@[W._-]+\.[W]+)>", mask):
                self.load_rule_template_and_replace_value("Email tester 2", profile, plan_file)
            elif re.match("W:([W._-]+@[W._-]+\.[W]+)", mask):
                self.load_rule_template_and_replace_value("Email tester 3", profile, plan_file)


    def generate_iban_rules(self, profile, plan_file):
        mask = profile.get_mask()
        if mask:
            if re.match("([L]{2}[D]{2}[DL]{11,27})", mask):
                self.load_rule_template_and_replace_value("IBAN validator 1", profile, plan_file)
            elif re.match("<([L]{2}[D]{2}[DL]{11,27})>", mask):
                self.load_rule_template_and_replace_value("IBAN validator 2", profile, plan_file)
            elif re.match("(\w+):([L]{2}[D]{2}[DL]{11,27})", mask):
                self.load_rule_template_and_replace_value("IBAN validator 3", profile, plan_file)
            elif re.match("(\w+):<([L]{2}[D]{2}[DL]{11,27})>", mask):
                self.load_rule_template_and_replace_value("IBAN validator 4", profile, plan_file)


    def generate_ipv4_rules(self, profile, plan_file):
        pattern = profile.get_pattern()
        if pattern:
            if pattern in RulesManager.ipv4_patterns:
                self.load_rule_template_and_replace_value("IPv4 Address validator", profile, plan_file)

    def generate_phone_rules(self, profile, plan_file):
        mask = profile.get_mask()
        if mask:
            if mask == '+N' or mask == '+N N N' or mask == '+N-N-N':
                self.load_rule_template_and_replace_value("Phone number tester", profile, plan_file)

    def load_rule_template_and_replace_value(self, rule_name, profile, plan_file):
        if rule_name == 'Field length':
            if profile.mask.isdigit():
                length = int(profile.mask)
            else:
                length = len(profile.mask)
        elif rule_name == 'Phone number tester':
            length = 10
        else:
            length = None
        rule = self.get_rule_by_name(rule_name)
        rule_expression_template = Template(rule['expression'])
        rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name, length=length)
        self.write_rule(plan_file, rule_name, rule_expression)


