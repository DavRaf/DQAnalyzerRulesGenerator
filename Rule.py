class Rule:

    def __init__(self, rule_name, rule_expression, rule_description):
        self.rule_name = rule_name
        self.rule_expression = rule_expression
        self.rule_description = rule_description

    def __eq__(self, other):
        return self.rule_expression == other.rule_expression

    def __hash__(self):
        return hash(('expression', self.rule_expression))
