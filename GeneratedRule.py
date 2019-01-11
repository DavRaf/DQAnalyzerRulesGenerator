class GeneratedRule:

    def __init__(self, column_name=None, pattern_value=None, pattern_num_cases=None, pattern_percent=None, rule_name=None, rule_description=None, rule_pattern=None, rule_expression=None):
        self.column_name = column_name
        self.pattern_value = pattern_value
        self.pattern_num_cases = pattern_num_cases
        self.pattern_percent = pattern_percent
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.rule_pattern = rule_pattern
        self.rule_expression = rule_expression

    def __eq__(self, other):
        return self.rule_name == other.rule_name

    def __hash__(self):
        return hash((self.rule_name))
