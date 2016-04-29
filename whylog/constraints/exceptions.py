from whylog.exceptions import WhylogError


class ConstraintError(WhylogError):
    pass


class ConstructorParamsError(ConstraintError):
    def __init__(self, constraint_type, correct_param_names, incorrect_param_names):
        self.constraint_type = constraint_type
        self.correct_params_names = correct_param_names
        self.incorrect_params_names = incorrect_param_names

    def __str__(self):
        return 'Wrong params names in constraint constructor: %s, actual names: %s, should be: %s' % (
            self.constraint_type, self.incorrect_params_names, self.correct_params_names
        )


class ConstructorGroupsCountError(ConstraintError):
    def __init__(self, constraint_type, groups_count, minimal_groups_count, maximal_groups_count):
        self.constraint_type = constraint_type
        self.groups_count = groups_count
        self.minimal_groups_count = minimal_groups_count
        self.maximal_groups_count = maximal_groups_count

    def __str__(self):
        return 'Wrong groups count in constraint: %s, has %s groups, should be at least: %s, at most %s' % (
            self.constraint_type, self.groups_count, self.minimal_groups_count,
            self.maximal_groups_count
        )


class VerificatedParamsError(ConstraintError):
    def __init__(self, constraint_type, params):
        self.constraint_type = constraint_type
        self.params = params

    def __str__(self):
        return "Wrong params while verification, params: %s" % (self.params,)
