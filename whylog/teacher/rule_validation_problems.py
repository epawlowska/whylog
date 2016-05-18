import itertools

from collections import namedtuple

ValidationResult = namedtuple('ValidationResult', ['errors', 'warnings'])


class ValidationResult(object):
    def __init__(self, errors, warnings):
        self.errors = errors
        self.warnings = warnings

    @classmethod
    def result_from_results(cls, results):
        errors = sorted(itertools.chain(*[result.errors for result in results]))
        warnings = sorted(itertools.chain(*[result.warnings for result in results]))
        return ValidationResult(errors, warnings)

    def is_successful(self):
        return not self.errors and not self.warnings

    def __str__(self):
        return "errors: \n" + str([str(error) for error in self.errors]) + \
               "\nwarnings: \n" + str([str(warning) for warning in self.warnings])


class RuleValidationProblem(object):
    pass


class ConstraintValidationProblem(RuleValidationProblem):
    pass


class PatternValidationProblem(RuleValidationProblem):
    pass


class NotUniqueParserName(RuleValidationProblem):
    def __init__(self, line_id):
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Parser name is not unique, line id: %s' % (self.line_id,)


class WrongLogType(RuleValidationProblem):
    def __init__(self, line_id):
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Log type is not chosen, line id: %s' % (self.line_id,)


class WrongPrimaryKey(RuleValidationProblem):
    def __init__(self, primary_key, group_numbers, line_id):
        self.primary_key = primary_key
        self.group_numbers = group_numbers
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Primary key %s should be subset of pattern groups %s, line id: %s' % \
               (self.primary_key, self.group_numbers, self.line_id)
