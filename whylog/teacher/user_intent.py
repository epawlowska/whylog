#TODO more unniversal: pattern_name, pattern
class UserParserIntent(object):
    def __init__(self, regex_name, regex, sample_line, log_type_name, primary_key_groups, data_conversions=None):
        self.regex_name = regex_name
        self.regex = regex
        self.sample_line = sample_line
        self.log_type_name = log_type_name
        self.primary_key_groups = primary_key_groups
        self.data_conversions = data_conversions or {}


class UserConstraintIntent(object):
    def __init__(self, constr_type, groups, params=None):
        self.type = constr_type
        self.groups = groups
        self.params = params or {}


class UserRuleIntent(object):
    def __init__(self, effect_id, parsers=None, constraints=None):
        self.effect_id = effect_id
        self.parsers = parsers or {}
        self.constraints = constraints or []
