import json

class DataProfile:

    def __init__(self, expression_name = None, expression_type = None, domain_analysis = [], statistics = [], mask_analysis = [], domain_name = None):
        self.expression_name = expression_name
        self.expression_type = expression_type
        self.domain_analysis = domain_analysis
        self.statistics = statistics
        self.mask_analysis = mask_analysis
        self.domain_name = domain_name
        self.pattern = None
        self.mask = None

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

    def get_pattern(self):
        if self.domain_analysis:
            num_cases_list = []
            for d_a in self.domain_analysis:
                num_cases_list.append(int(d_a.num_cases))
            max_num_cases = max(num_cases_list)
            for d_a in self.domain_analysis:
                if int(d_a.num_cases) == max_num_cases:
                    pattern = d_a.value
            if pattern is None:
                second_largest = sorted(set(num_cases_list))[-2]
                for d_a in self.domain_analysis:
                    if int(d_a.num_cases) == second_largest:
                        pattern = d_a.value
            self.set_pattern(pattern)
            return pattern
        return None

    def get_mask(self):
        if self.mask_analysis:
            mask_analysis_list = []
            mask_analysis = self.mask_analysis
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
            self.set_mask(mask)
            return mask
        return None

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