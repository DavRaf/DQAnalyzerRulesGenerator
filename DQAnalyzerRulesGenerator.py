from RulesManager import RulesManager
from XMLFileManager import XMLFileManager
from bson.objectid import ObjectId
from string import Template
import re

xml_file_manager = XMLFileManager()
profiles, profiles_in_json = xml_file_manager.read_profile('test-iban.txt.profile.xml')
'''for p in profiles_in_json:
    print(p + '\n')'''
files = ['expressions.common.templates', 'expressions.usc.templates', 'regex.common.templates']
rules_templates = xml_file_manager.read_rules_expressions_advanced(files)
'''for r in rules_templates:
    print(r + '\n')'''
rules_manager = RulesManager()
profile = profiles[0]
#print(profile.mask_analysis)
domain = profile.domain_name
expression_type = profile.expression_type
domain_analysis = profile.domain_analysis
num_cases_list = []

# date rules
if 'string' in expression_type.casefold() and 'day' in domain.casefold():
    for d_a in domain_analysis:
        num_cases_list.append(int(d_a.num_cases))
        # values.append(d_a.value)
    max_num_cases = max(num_cases_list)
    for d_a in domain_analysis:
        if int(d_a.num_cases) == max_num_cases:
            pattern = d_a.value
    if pattern == 'N-N-N':
        rule1 = rules_manager.get_rule_by_name("US Date format YYYY-mm-DD")
        rule2 = rules_manager.get_rule_by_name("EU Date format DD-mm-YYYY")
        rule_expression_template1 = rule1['expression']
        rule_expression_template2 = rule2['expression']
        rule_expression_template1 = Template(rule_expression_template1)
        rule_expression_template2 = Template(rule_expression_template2)
        rule_expression1 = rule_expression_template1.safe_substitute(value= profile.expression_name)
        rule_expression2 = rule_expression_template2.safe_substitute(value= profile.expression_name)
        #xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule1["name"], rule_expression1)
        xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule2["name"], rule_expression2)
    elif pattern == 'N/N/N':
        rule1 = rules_manager.get_rule_by_name("US Date format YYYY/mm/DD")
        rule2 = rules_manager.get_rule_by_name("EU Date format DD/mm/YYYY")
        rule_expression_template1 = rule1['expression']
        rule_expression_template2 = rule2['expression']
        rule_expression_template1 = Template(rule_expression_template1)
        rule_expression_template2 = Template(rule_expression_template2)
        rule_expression1 = rule_expression_template1.safe_substitute(value= profile.expression_name)
        rule_expression2 = rule_expression_template2.safe_substitute(value= profile.expression_name)
        #xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule1["name"], rule_expression1)
        xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule2["name"], rule_expression2)
    elif pattern == 'N.N.N':
        rule1 = rules_manager.get_rule_by_name("US Date format YYYY.mm.DD")
        rule2 = rules_manager.get_rule_by_name("EU Date format DD.mm.YYYY")
        rule_expression_template1 = rule1['expression']
        rule_expression_template2 = rule2['expression']
        rule_expression_template1 = Template(rule_expression_template1)
        rule_expression_template2 = Template(rule_expression_template2)
        rule_expression1 = rule_expression_template1.safe_substitute(value= profile.expression_name)
        rule_expression2 = rule_expression_template2.safe_substitute(value= profile.expression_name)
        #xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule1["name"], rule_expression1)
        xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule2["name"], rule_expression2)

# sin rules
profile = profiles[0]
mask_analysis_list = []
mask_analysis = profile.mask_analysis
for m in mask_analysis:
    mask_analysis_list.append(int(m.count))
if mask_analysis_list:
    mask_analysis_count_max = max(mask_analysis_list)
    for m in mask_analysis:
        if int(m.count) == mask_analysis_count_max:
         mask = m.value
    if len(mask) == 9:
        if mask == 'DDDDDDDDD' or mask == 'LLL: DDDDDDDD' or mask == 'DDD-DDD-DDD' or mask == 'DDD DDD DDD' or mask == 'LLLDDDDDDDDD' or mask == 'LLL:DDDDDDDDD':
            rule = rules_manager.get_rule_by_name("SSN")
            rule_expression_template = rule['expression']
            rule_expression_template = Template(rule_expression_template)
            rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
            xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule["name"], rule_expression)

# fiscal code rules
profile = profiles[0]
mask_analysis_list = []
mask_analysis = profile.mask_analysis
for m in mask_analysis:
    mask_analysis_list.append(int(m.count))
mask_analysis_count_max = max(mask_analysis_list)
for m in mask_analysis:
    if int(m.count) == mask_analysis_count_max:
        mask = m.value
if len(mask) == 16:
    if mask == 'LLLLLLDDLDDLDDDL' or mask == 'LL:LLLLLLDDLDDLDDDL':
        rule = rules_manager.get_rule_by_name("Fiscal Code")
        rule_expression_template = rule['expression']
        rule_expression_template = Template(rule_expression_template)
        rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
        xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule["name"], rule_expression)

# number rules
profile = profiles[0]
domain_analysis = profile.domain_analysis
num_cases_list = []
if 'integer' not in profile.domain_name:
    for d_a in domain_analysis:
        num_cases_list.append(int(d_a.num_cases))
        # values.append(d_a.value)
    if num_cases_list:
        max_num_cases = max(num_cases_list)
        for d_a in domain_analysis:
            if int(d_a.num_cases) == max_num_cases:
                pattern = d_a.value
    mask_analysis_list = []
    mask_analysis = profile.mask_analysis
    for m in mask_analysis:
        mask_analysis_list.append(int(m.count))
    if mask_analysis_list:
        mask_analysis_count_max = max(mask_analysis_list)
        for m in mask_analysis:
            if int(m.count) == mask_analysis_count_max:
                mask = m.value
        if mask is None:
            second_largest = sorted(set(mask_analysis_list))[-2]
            for m in mask_analysis:
                if int(m.count) == second_largest:
                    mask = m.value
    #print(pattern, mask)
    '''if pattern == 'N' or pattern == 'W':
        rule = rules_manager.get_rule_by_name("Field length")
        rule_expression_template = rule['expression']
        rule_expression_template = Template(rule_expression_template)
        rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name, length=len(mask))
        xml_file_manager.write_rule_advanced('1.2 Advanced.plan', rule["name"], rule_expression)'''

# email rules
profile = profiles[0]
mask_analysis_list = []
mask_analysis = profile.mask_analysis
for m in mask_analysis:
    mask_analysis_list.append(int(m.count))
mask_analysis_count_max = max(mask_analysis_list)
for m in mask_analysis:
    if int(m.count) == mask_analysis_count_max:
        mask = m.value
if mask is None:
    second_largest = sorted(set(mask_analysis_list))[-2]
    for m in mask_analysis:
        if int(m.count) == second_largest:
            mask = m.value
if re.match("([W._-]+@[W._-]+\.[W]+)", mask):
    rule = rules_manager.get_rule_by_name("Email tester 1")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('2.1 Email Parsing.plan', rule["name"], rule_expression)
elif re.match("<([W._-]+@[W._-]+\.[W]+)>", mask):
    rule = rules_manager.get_rule_by_name("Email tester 2")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('2.1 Email Parsing.plan', rule["name"], rule_expression)
elif re.match("W:([W._-]+@[W._-]+\.[W]+)", mask):
    rule = rules_manager.get_rule_by_name("Email tester 3")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('2.1 Email Parsing.plan', rule["name"], rule_expression)

'''# phone rules
profile = profiles[0]
mask_analysis_list = []
mask_analysis = profile.mask_analysis
for m in mask_analysis:
    mask_analysis_list.append(int(m.count))
mask_analysis_count_max = max(mask_analysis_list)
for m in mask_analysis:
    if int(m.count) == mask_analysis_count_max:
        mask = m.value
if mask is None:
    second_largest = sorted(set(mask_analysis_list))[-2]
    for m in mask_analysis:
        if int(m.count) == second_largest:
            mask = m.value
if mask == '+N' or mask == '+N N N' or mask == '+N-N-N':
    rule = rules_manager.get_rule_by_name("Phone number tester") #Cleanse and format US phone number
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name, length=10) #update with stat
    xml_file_manager.write_rule_advanced('2.1 Email Parsing.plan', rule["name"], rule_expression)'''

# iban rules
profile = profiles[1]
mask_analysis_list = []
mask_analysis = profile.mask_analysis
for m in mask_analysis:
    mask_analysis_list.append(int(m.count))
mask_analysis_count_max = max(mask_analysis_list)
for m in mask_analysis:
    if int(m.count) == mask_analysis_count_max:
        mask = m.value
if mask is None:
    second_largest = sorted(set(mask_analysis_list))[-2]
    for m in mask_analysis:
        if int(m.count) == second_largest:
            mask = m.value
if re.match("([a-zA-Z]{4}\s?[a-zA-Z]{11,27})", mask):
    rule = rules_manager.get_rule_by_name("IBAN validator 1")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('test-iban.txt.plan', rule["name"], rule_expression)
elif re.match("<([a-zA-Z]{4}\s?[a-zA-Z]{11,27})>", mask):
    rule = rules_manager.get_rule_by_name("IBAN validator 2")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('test-iban.txt.plan', rule["name"], rule_expression)
elif re.match("(\w+):([a-zA-Z]{4}\s?[a-zA-Z]{11,27})", mask):
    rule = rules_manager.get_rule_by_name("IBAN validator 3")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('test-iban.txt.plan', rule["name"], rule_expression)
elif re.match("(\w+):<([a-zA-Z]{4}\s?[a-zA-Z]{11,27})>", mask):
    rule = rules_manager.get_rule_by_name("IBAN validator 4")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('test-iban.txt.plan', rule["name"], rule_expression)

# ipv4 rules
profile = profiles[2]
num_cases_list = []
domain_analysis = profile.domain_analysis
for d_a in domain_analysis:
    num_cases_list.append(int(d_a.num_cases))
    # values.append(d_a.value)
if num_cases_list:
    max_num_cases = max(num_cases_list)
    for d_a in domain_analysis:
        if int(d_a.num_cases) == max_num_cases:
            pattern = d_a.value
if pattern == 'N.N.N.N' or pattern == 'D.D.D.D' or pattern == 'N.D.D.D' or pattern == 'N.N.D.D' or pattern == 'N.N.N.D' or pattern == 'D.N.N.N' or pattern == 'D.D.N.N' or pattern == 'D.D.D.N' or pattern == 'N.D.N.D' or pattern == 'D.N.D.N' or pattern == 'N.D.D.N' or pattern == 'D.N.N.D':
    rule = rules_manager.get_rule_by_name("IPv4 Address validator")
    rule_expression_template = rule['expression']
    rule_expression_template = Template(rule_expression_template)
    rule_expression = rule_expression_template.safe_substitute(value=profile.expression_name)
    xml_file_manager.write_rule_advanced('test-iban.txt.plan', rule["name"], rule_expression)
#rules_manager.get_all_rules()
#rules_manager.get_rule_by_id_and_replace_value(ObjectId("5bf3d6a86672568be9693ea6"))
#print(len(rules_templates))
#xml_file_manager.write_rule('1.2 Advanced.plan')