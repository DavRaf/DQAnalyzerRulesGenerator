from xml.dom import minidom
from DataProfile import DataProfile
from DomainAnalyse import DomainAnalyse
from MaskAnalysis import MaskAnalysis
from MongoDBManager import MongoDBManager
from Rule import Rule
from RuleTemplate import RuleTemplate
from StatisticsData import StatisticsData
import html
import pickle

class XMLFileManager:

    DATA_ANALYSE = 'dataAnalyse'
    COLUMN = 'column'
    COLUMN_TYPE = 'columnType'
    EXPRESSION = 'expression'
    EXAMPLES = 'examples'
    EXAMPLE = 'example'
    NUM_CASES = 'numCases'
    VALUE = 'value'
    STATISTICS = 'statistics'
    STAT ='stat'
    ITEM = 'item'
    TYPE = 'type'
    BUSINESS_RULE = 'businessRule'
    BUSINESS_RULES = 'businessRules'
    NAME = 'name'

    def __init__(self):
        self.mongodb_manager = MongoDBManager()

    def read_profile(self, file):
        doc = minidom.parse(file)
        profiles = []
        profiles_in_json = []
        domain_analysis = []
        statistics_data_list = []
        mask_analyses = []
        domain_names = []
        data_analyses = doc.getElementsByTagName(XMLFileManager.DATA_ANALYSE)
        for d_a in data_analyses:
            if XMLFileManager.COLUMN_TYPE in d_a.attributes:
                profile = DataProfile()
                expression_type = d_a.attributes[XMLFileManager.COLUMN_TYPE].value
                profile.set_expression_type(expression_type)
                domain = d_a.getElementsByTagName("domainAnalyse")
                for d in domain:
                    domain_name = d.attributes['name'].value
                    domain_names.append(domain_name)
                profile.set_domain_name(' '.join(domain_names))
                domain_names = []
                expressions = d_a.getElementsByTagName(XMLFileManager.EXPRESSION)
                for expression in expressions:
                    expression_name = expression.firstChild.data
                    profile.set_expression_name(expression_name)
                examples = d_a.getElementsByTagName(XMLFileManager.EXAMPLES)
                for example in examples:
                    ex = example.getElementsByTagName(XMLFileManager.EXAMPLE)
                    for e in ex:
                        domain_analyse = DomainAnalyse(e.attributes[XMLFileManager.NUM_CASES].value, e.attributes[XMLFileManager.VALUE].value)
                        domain_analysis.append(domain_analyse)
                    profile.set_domain_analysis(domain_analysis)
                domain_analysis = []
                statistics = d_a.getElementsByTagName(XMLFileManager.STATISTICS)
                for statistic in statistics:
                    stat = statistic.getElementsByTagName(XMLFileManager.STAT)
                    for st in stat:
                        item = st.getElementsByTagName(XMLFileManager.ITEM)
                        for i in item:
                            if st.attributes[XMLFileManager.TYPE].value in ('count', 'count_nulls', 'count_not_nulls', 'unique', 'non_unique', 'duplicate'):
                                statistics_data = StatisticsData(st.attributes[XMLFileManager.TYPE].value, i.attributes[XMLFileManager.VALUE].value)
                                statistics_data_list.append(statistics_data)
                        profile.set_statistics(statistics_data_list)
                    statistics_data_list = []
                frequencies_masked = d_a.getElementsByTagName("frequenciesMasked")
                for f_m in frequencies_masked:
                    mask_item = f_m.getElementsByTagName(XMLFileManager.ITEM)
                    for m_i in mask_item:
                        mask_item_count = m_i.attributes['count'].value
                        mask_item_percent = m_i.attributes['percent'].value
                        if 'value' in m_i.attributes:
                            mask_item_value = m_i.attributes['value'].value
                        else:
                            mask_item_value = None
                        mask_analysis = MaskAnalysis(mask_item_count, mask_item_percent, mask_item_value)
                        mask_analyses.append(mask_analysis)
                    profile.set_mask_analysis(mask_analyses)
                    mask_analyses = []
                profiles.append(profile)
        for profile in profiles:
            profiles_in_json.append(profile.to_json())
        return profiles, profiles_in_json

    def read_rules_expressions_advanced(self, file):
        rules_templates = []
        doc = minidom.parse(file)
        templates = doc.getElementsByTagName('template')
        for template in templates:
            name = template.attributes['name'].value
            description = template.attributes['description'].value
            expression = template.attributes['expression'].value
            pattern = template.attributes['pattern'].value
            expression = html.unescape(expression).replace("\n", "").replace("\t", "")
            temp = RuleTemplate(name, description, expression, pattern)
            rules_templates.append(temp.to_json())
            self.mongodb_manager.collection.update({"name": name}, {"$set":{"name" : name,
                                        "description": description,
                                        "expression": expression,
                                        "pattern": pattern}}, upsert = True)
        return rules_templates

    def write_rule_advanced(self, file, rule_name, rule_expression):
        doc = minidom.parse(file)
        element = doc.createElement(XMLFileManager.BUSINESS_RULE)
        element.setAttribute(XMLFileManager.EXPRESSION, rule_expression)
        element.setAttribute(XMLFileManager.NAME, rule_name)
        cd = doc.getElementsByTagName(XMLFileManager.BUSINESS_RULES)[0]
        cd.appendChild(element)
        doc.writexml(open(file, "w"))




