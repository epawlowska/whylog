from collections import namedtuple

from whylog.assistant.validation_problems import WrongConverterProblem
from whylog.converters import CONVERTION_MAPPING, STRING
from whylog.converters.exceptions import UnsupportedConverterError
from whylog.teacher.rule_validation_problems import ValidationResult

PatternMatch = namedtuple('PatternMatch', ['line_text', 'pattern', 'param_groups'])


class ParamGroup(object):
    def __init__(self, content, converter):
        self.content = content
        self.converter = converter

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def validate_converter(self, line_id):
        group_content = self.content
        converter_type = self.converter
        if converter_type == STRING:
            return ValidationResult(errors=[], warnings=[])
        errors = []
        converter = CONVERTION_MAPPING.get(converter_type)
        if converter is None:
            # This should never happen since converter_type is proposed to user by Front
            raise UnsupportedConverterError(converter_type)
        try:
            converter.convert(group_content)
        except ValueError:
            errors.append(WrongConverterProblem(group_content, converter_type, line_id))
        return ValidationResult(errors=errors, warnings=[])
