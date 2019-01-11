from xml.dom import minidom
from xml.etree import ElementTree as ET
from DataProfile import DataProfile
from DomainAnalysis import DomainAnalysis
from MaskAnalysis import MaskAnalysis
from MongoDBManager import MongoDBManager
from GeneratedRule import GeneratedRule
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
    DATE_FORMAT = 'date_format'

    def __init__(self):
        self.mongodb_manager = MongoDBManager()

    def read_profile(self, file):
        doc = minidom.parse(file)
        profiles = []
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
                        domain_analyse = DomainAnalysis(int(e.attributes[XMLFileManager.NUM_CASES].value), e.attributes[XMLFileManager.VALUE].value)
                        domain_analysis.append(domain_analyse)
                    profile.set_domain_analysis(domain_analysis)
                domain_analysis = []
                statistics = d_a.getElementsByTagName(XMLFileManager.STATISTICS)
                for statistic in statistics:
                    stat = statistic.getElementsByTagName(XMLFileManager.STAT)
                    for st in stat:
                        item = st.getElementsByTagName(XMLFileManager.ITEM)
                        for i in item:
                            if st.attributes[XMLFileManager.TYPE].value in ('count', 'count_nulls', 'count_not_nulls', 'distinct', 'min', 'max', 'median', 'unique', 'non_unique', 'duplicate'):
                                statistics_data = StatisticsData(st.attributes[XMLFileManager.TYPE].value, i.attributes[XMLFileManager.VALUE].value)
                                statistics_data_list.append(statistics_data)
                        profile.set_statistics(statistics_data_list)
                    statistics_data_list = []
                frequencies_masked = d_a.getElementsByTagName("frequenciesMasked")
                for f_m in frequencies_masked:
                    mask_item = f_m.getElementsByTagName(XMLFileManager.ITEM)
                    for m_i in mask_item:
                        mask_item_count = int(m_i.attributes['count'].value)
                        mask_item_percentage = float(m_i.attributes['percent'].value.replace("%", ""))
                        if 'value' in m_i.attributes:
                            mask_item_value = m_i.attributes['value'].value
                        else:
                            mask_item_value = None
                        mask_analysis = MaskAnalysis(mask_item_count, mask_item_percentage, mask_item_value)
                        mask_analyses.append(mask_analysis)
                    profile.set_mask_analysis(mask_analyses)
                    mask_analyses = []
                profiles.append(profile)
        return profiles

    def read_rules_expressions_advanced(self, file):
        doc = minidom.parse(file)
        templates = doc.getElementsByTagName('template')
        for template in templates:
            name = template.attributes['name'].value
            description = template.attributes['description'].value
            expression = template.attributes['expression'].value
            pattern = template.attributes['pattern'].value
            expression = html.unescape(expression).replace("\n", "").replace("\t", "")
            category = template.attributes['category'].value
            if XMLFileManager.DATE_FORMAT in template.attributes:
                date_format = template.attributes['date_format'].value
            temp = RuleTemplate(name, description, expression, pattern)
            self.mongodb_manager.collection.update({"name": name}, {"$set":{"name" : name,
                                        "description": description,
                                        "expression": expression,
                                        "pattern": pattern,
                                        "category": category,
                                        "date_format": date_format}}, upsert = True)

    def read_rules_from_plan_file(self, file):
        doc = minidom.parse(file)
        rules = doc.getElementsByTagName('businessRule')
        rules_list = list()
        for rule in rules:
            name = rule.attributes['name'].value
            expression = rule.attributes['expression'].value
            expression = html.unescape(expression).replace("\n", "").replace("\t", "")
            generated_rule = GeneratedRule(column_name=expression.split('\"')[2], rule_name=name, rule_expression=expression)
            rules_list.append(generated_rule)
        return rules_list

    def read_field_names_in_plan_file(self, file):
        field_names = []
        doc = minidom.parse(file)
        fields = doc.getElementsByTagName('textReaderColumn')
        for field in fields:
            field_name = field.attributes['name'].value
            field_names.append(field_name)
        return field_names

    def read_transformers(self):
        transformers_names = list()
        doc = minidom.parse('corrections.xml')
        transformers = doc.getElementsByTagName('transformer')
        for transformer in transformers:
            transformer_name = transformer.attributes['name'].value
            transformers_names.append(transformer_name)
        return transformers_names

    def read_dataset_name(self, file):
        doc = minidom.parse(file)
        tags = doc.getElementsByTagName('properties')
        for tag in tags:
            if 'fileName' in tag.attributes:
                dataset_name = tag.attributes['fileName'].value
        return dataset_name

    def write_rule_advanced(self, file, rule_name, rule_expression):
        doc = minidom.parse(file)
        element = doc.createElement(XMLFileManager.BUSINESS_RULE)
        element.setAttribute(XMLFileManager.EXPRESSION, rule_expression)
        element.setAttribute(XMLFileManager.NAME, rule_name)
        cd = doc.getElementsByTagName(XMLFileManager.BUSINESS_RULES)[0]
        cd.appendChild(element)
        doc.writexml(open(file, "w"))

    def save_to_xml_file(self, file):
        ET.register_namespace('', "http://eobjects.org/analyzerbeans/job/1.0")
        tree = ET.XML(file)
        with open("remediation.analysis.xml", "wb") as f:
            f.write(ET.tostring(tree))




