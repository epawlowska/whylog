from whylog.teacher.rule_validation_problems import ConstraintValidationProblem
from whylog.constraints import TimeConstraint


class ConstraintVerificationFail(ConstraintValidationProblem):
    def __init__(self, constraint_type, params, group_contents):
        self.constraint_type = constraint_type
        self.params = params
        self.group_contents = group_contents

    def __str__(self):
        return 'Constraint verification failed, constraint type: %s, params: %s, groups: %s' % \
               (self.constraint_type, self.params, self.group_contents)


class TimeConstraintValidationProblem(ConstraintValidationProblem):
    pass


class WrongTimeDeltas(TimeConstraintValidationProblem):
    def __init__(self, min_time_delta, max_time_delta):
        self.constraint_type = TimeConstraint.TYPE
        self.min_time_delta = min_time_delta
        self.max_time_delta = max_time_delta

    def __str__(self):
        return 'Validation problem in Constraint: %s. Min time delta: %s should be lower than Max time delta: %s' % \
               (self.constraint_type, self.min_time_delta, self.max_time_delta)
