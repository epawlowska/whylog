from whylog.teacher.rule_validation_problems import PatternValidationProblem


class NotMatchingPatternProblem(PatternValidationProblem):
    def __init__(self, line_id):
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Pattern does not match line, line id: %s' % (self.line_id,)


class WrongConverterProblem(PatternValidationProblem):
    def __init__(self, group_no, converter, line_id):
        self.group_no = group_no
        self.converter = converter
        self.line_id = line_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return 'Wrong group converter, converter: %s, group: %s, line id: %s' %\
               (self.converter, self.group_no, self.line_id)