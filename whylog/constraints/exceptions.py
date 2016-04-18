from whylog.exceptions import WhylogError


class VerificationError(WhylogError):
    pass


class UnsupportedConstraintTypeError(VerificationError):
    def __init__(self, constraint_data):
        self._constraint_data = constraint_data

    def __str__(self):
        return "No such constraint (%s) registered" % self._constraint_data['name']

class ConstraintError(WhylogError):
    pass


class ConstructorParamsError(ConstraintError):
    def __init__(self, constraint_type, correct_param_names, incorrect_param_names):
        self.constraint_type = constraint_type
        self.correct_params_names = correct_param_names
        self.incorrect_params_names = incorrect_param_names

    def __str__(self):
        return 'Incorrect keys in constructor params dict in constraint: %s, actual keys: %s, should be: %s' % (
            self.constraint_type, self.incorrect_params_names.keys(),
            self.correct_params_names.keys()
        )


class ConstructorGroupsError(ConstraintError):
    def __init__(self, constraint_type, groups_count, minimal_groups_count, maximal_groups_count):
        self.constraint_type = constraint_type
        self.groups_count = groups_count
        self.minimal_groups_count = minimal_groups_count
        self.maximal_groups_count = maximal_groups_count

    def __str__(self):
        return 'Incorrect groups count in constraint: %s, has %s groups, should be at least: %s, at most %s' % (
            self.constraint_type, self.groups_count, self.minimal_groups_count,
            self.maximal_groups_count
        )
