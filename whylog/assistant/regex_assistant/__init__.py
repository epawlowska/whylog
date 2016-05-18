import six

from whylog.assistant import AbstractAssistant
from whylog.assistant.const import AssistantType
from whylog.assistant.regex_assistant.regex_match import RegexMatch
from whylog.teacher.rule_validation_problems import ValidationResult


class RegexAssistant(AbstractAssistant):
    """
    Responsible for creating regex for each line of Rule.
    RegexAssistant helps user to write regex, it can also propose regex.
    One RegexAssistant per one entering Rule.

    :type regex_matches: dict[int, RegexMatch]
    """

    TYPE = AssistantType.REGEX

    def __init__(self):
        self.regex_matches = {}

    def add_line(self, line_id, line_object):
        regex_match = RegexMatch(line_id, line_object)
        self.regex_matches[line_id] = regex_match

    def remove_line(self, line_id):
        del self.regex_matches[line_id]

    def get_pattern_match(self, line_id):
        regex_match = self.regex_matches[line_id]
        return regex_match.convert_to_pattern_match()

    def update_by_pattern(self, line_id, pattern):
        self.regex_matches[line_id].update_by_regex(pattern)

    def update_by_guessed_pattern_match(self, line_id, regex_id):
        self.regex_matches[line_id].update_by_guessed_regex(regex_id)

    def guess_pattern_matches(self, line_id):
        regex_match = self.regex_matches[line_id]
        return regex_match.guessed_pattern_matches

    def set_converter(self, line_id, group_no, converter):
        self.regex_matches[line_id].set_converter(group_no, converter)

    def validate(self):
        validation_results = [
            regex_match.validate() for regex_match in six.itervalues(self.regex_matches)
        ]
        return ValidationResult.result_from_results(validation_results)
