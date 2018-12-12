class NewPattern:

    def __init__(self, column_name, pattern_value, pattern_num_cases, pattern_percent):
        self.column_name = column_name
        self.pattern_value = pattern_value
        self.pattern_num_cases = pattern_num_cases
        self.pattern_percent = pattern_percent

    def __eq__(self, other):
        return self.pattern_value == other.pattern_value and self.column_name == other.column_name

    def __hash__(self):
        return hash((self.pattern_value, self.column_name))