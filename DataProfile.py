class DataProfile:

    def __init__(self, expression_name = None, expression_type = None, domain_analysis = [], statistics = [], mask_analysis = [], domain_name = None):
        self.expression_name = expression_name
        self.expression_type = expression_type
        self.domain_analysis = domain_analysis
        self.statistics = statistics
        self.mask_analysis = mask_analysis
        self.domain_name = domain_name

    def set_expression_name(self, expression_name):
        self.expression_name = expression_name

    def set_expression_type(self, expression_type):
        self.expression_type = expression_type

    def set_domain_analysis(self, domain_analysis):
        self.domain_analysis = domain_analysis

    def set_statistics(self, statistics):
        self.statistics = statistics

    def set_mask_analysis(self, mask_analysis):
        self.mask_analysis = mask_analysis

    def set_domain_name(self, domain_name):
        self.domain_name = domain_name

    def set_pattern(self, pattern):
        self.pattern = pattern

    def set_mask(self, mask):
        self.mask = mask