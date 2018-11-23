import json

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

    '''def print_profile(self):
        print('Profile: \n')
        print(self.expression_name + '\n')
        print(self.expression_type + '\n')
        if self.domain_analysis:
            for p in self.domain_analysis:
                print(p.num_cases)
                print(p.value)
        for s in self.statistics:
            print(s.type)
            print(s.value)'''


    '''def __str__(self):
        return "Profile: {\n" \
               " expression name: " + self.expression_name + ", \n" \
               " expression type: " + self.expression_type + ", \n" \
               " domain name: " + self.domain_name + ", \n" \
               " domain_analysis: " + self.domain_analysis.__str__() + ", \n" \
               " statistics: " + " ".join(self.statistics).__str__() + ", \n" \
               " mask analysis: " + " ".join(self. mask_analysis).__str__() + "\n}"'''

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)