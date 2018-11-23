import json

class RuleTemplate:

    def __init__(self, name = None, description = None, expression = None, category = None):
        self.name = name
        self.description = description
        self.expression = expression
        self.category = category

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_expression(self, expression):
        self.expression = expression

    def set_category(self, category):
        self.category = category

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)