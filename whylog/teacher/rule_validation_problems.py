from collections import namedtuple


ValidationResult = namedtuple('ValidationResult', ['errors', 'warnings'])


class RuleValidationProblem(object):
    pass


class ConstraintValidationProblem(RuleValidationProblem):
    pass


class NotMatchingPattern(RuleValidationProblem):
    def __init__(self, line, pattern):
        self.line = line
        self.pattern = pattern

    def __str__(self):
        return 'Pattern does not match line, pattern: %s, line: %s' % (self.pattern, self.line)


class NotUniqueParserName(RuleValidationProblem):
    def __init__(self, parser_name):
        self.parser_name = parser_name

    def __str__(self):
        return 'Name is not unique, name: %s' % (self.parser_name,)


