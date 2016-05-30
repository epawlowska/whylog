import itertools

import six

from whylog.assistant.validation_problems import WrongConverterProblem, InvalidPrimaryKeyProblem
from whylog.converters import get_converter
from whylog.converters.exceptions import ConverterError


class PatternMatch(object):
    def __init__(self, line_text, pattern, param_groups, primary_key=None):
        self.line_text = line_text
        self.pattern = pattern
        self.param_groups = param_groups  # dict[int, ParamGroup]
        self.primary_key = primary_key
        if primary_key is None:
            if not self.param_groups:
                self.primary_key = []
            else:
                self.primary_key = [min(self.param_groups.keys())]

    def validate_primary_key(self):
        group_numbers = self.param_groups.keys()
        if set(group_numbers) - set(self.primary_key):
            return [InvalidPrimaryKeyProblem(self.primary_key, group_numbers)]
        return []

    def validate_converters(self):
        return list(itertools.chain.from_iterable([
            param_group.validate_converter()
            for param_group in six.itervalues(self.param_groups)
        ]))


class ParamGroup(object):
    def __init__(self, content, converter):
        self.content = content
        self.converter = converter

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def validate_converter(self):
        group_content = self.content
        converter_type = self.converter
        converter = get_converter(converter_type)
        try:
            converter.safe_convert(group_content)
        except ConverterError:
            return [WrongConverterProblem(group_content, converter_type)]
        return []
