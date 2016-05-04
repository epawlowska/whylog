from collections import namedtuple

ParamGroup = namedtuple('ParamGroup', ['content', 'converter'])


class ParamGroup(object):
    def __init__(self, content, converter):
        self.content = content
        self.converter = converter

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class PatternMatch(object):
    """
    :type param_groups: dict[int, ParamGroup]
    """

    def __init__(self, line_text, pattern, param_groups):
        self.line_text = line_text
        self.pattern = pattern
        self.param_groups = param_groups
