import json

class RuleTemplate:

    def __init__(self, name = None, description = None, expression = None, pattern = None):
        self.name = name
        self.description = description
        self.expression = expression
        self.pattern = pattern

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_expression(self, expression):
        self.expression = expression

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)