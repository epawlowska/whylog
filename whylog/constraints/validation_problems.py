from whylog.teacher.rule_validation_problems import ConstraintValidationProblem


class ConstraintVerificationFail(ConstraintValidationProblem):
    def __init__(self, constraint_type, group_contents, params):
        self.constraint_type = constraint_type
        self.group_contents = group_contents
        self.params = params

    def __str__(self):
        return 'Constraint verification failed, constraint type: %s, params: %s, groups: %s' % \
               (self.constraint_type, self.params, self.group_contents)


class TimeConstraintValidationProblem(ConstraintValidationProblem):
    pass


class WrongTimeDeltas(TimeConstraintValidationProblem):
    def __init__(self, min_time_delta, max_time_delta):
        self.min_time_delta = min_time_delta
        self.max_time_delta = max_time_delta

    def __str__(self):
        return 'Validation problem in TimeConstraint: Min time delta: %s should be lower than Max time delta: %s' % \
               (self.min_time_delta, self.max_time_delta)
