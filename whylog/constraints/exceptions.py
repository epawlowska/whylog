from whylog.exceptions import WhylogError


class ConstraintError(WhylogError):
    pass


class ConstraintVerificationError(ConstraintError):
    def __init__(self, constr_type, param_dict, group_contents):
        self.constr_type = constr_type
        self.param_dict = param_dict
        self.group_contents = group_contents

    def __str__(self):
        return 'Constraint verification failed, constraint type: %s, params dict: %s, group contents %s' % (
            self.constr_type, self.param_dict, self.group_contents
        )


class ConstructorParamsError(ConstraintError):
    def __init__(self, correct_param_names, incorrect_param_names):
        self.correct_params_names = correct_param_names
        self.incorrect_params_names = incorrect_param_names

    def __str__(self):
        return 'Incorrect keys in constructor params dict, actual keys: %s, should be: %s' % (
            self.incorrect_params_names.keys(), self.correct_params_names.keys()
        )
