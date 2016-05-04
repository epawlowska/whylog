from whylog.assistant.const import DataType
from whylog.assistant.pattern_object import ParamGroup, PatternObject
from whylog.assistant.regex_assistant.guessing import guess_regex_objects
from whylog.assistant.regex_assistant.regex import create_obvious_regex, verify_regex


class RegexObject(object):
    """
    Container for information about line and corresponding regex
    Supports interactive updates like adding/removing groups to regex, replacing regex
    Keeps own data integrity - especially consistency between regex and groups (group_spans).
    Verifies updates.

    :param line_text: line text (raw string)
    :param param_groups: represents params from text (catched by regex groups)
    :param regex: regex matching to line_text
    :param guessed_pattern_objects: keeps guessed regexes that match to line_text
    :type param_groups: dict[int, ParamGroup]
    :type guessed_pattern_objects: dict[int, PatternObject]
    """

    def __init__(self, line_object):
        self.line_text = line_object.line_content
        self.param_groups = dict()

        self.regex = None
        self.update_by_regex(create_obvious_regex(self.line_text))

        self.guessed_pattern_objects = dict()
        self._guess_regexes()

    def convert_to_pattern_object(self):
        return PatternObject(self.line_text, self.regex, self.param_groups)

    def update_by_regex(self, new_regex):
        """
        Assigns self.regex to new_regex.

        Throws NotMatchingRegexError if new_regex doesn't match self.line_text
        If needed, improves new_regex: new_regex = '^' + new_regex + '$' (regex must match whole line)
        Updates self.param_groups so that they correspond to new_regex groups
        """

        groups = verify_regex(new_regex, self.line_text)

        if not new_regex[0] == '^':
            new_regex = '^' + new_regex
        if not new_regex[-1] == '$':
            new_regex += '$'

        default_converter = DataType.STRING
        self.param_groups = dict(
            [
                (
                    key + 1, ParamGroup(content, default_converter)
                ) for key, content in zip(
                    range(len(groups)), groups
                )
            ]
        )
        self.regex = new_regex

    def update_by_regex_object(self, regex_object):
        self.regex = regex_object.pattern
        self.param_groups = regex_object.param_groups

    def update_by_guessed_regex(self, regex_id):
        self.update_by_regex_object(self.guessed_pattern_objects[regex_id])

    def _guess_regexes(self):
        guessed_objects = guess_regex_objects(self.line_text)
        guessed_dict = dict(
            [
                (
                    key, regex_object
                ) for key, regex_object in zip(
                    range(len(guessed_objects)), guessed_objects
                )
            ]
        )
        self.guessed_pattern_objects = guessed_dict
        self.update_by_guessed_regex(regex_id=0)

    def set_converter(self, group_no, converter):
        #TODO: verify converter
        self.param_groups[group_no].converter = converter

    def verify(self):
        """
        Verifies properties such as:
        - regex matching a whole text
        - regex matching text in a one way only
        - group_spans converters (Span.converter) are proper
        If properties are not met, proper exceptions are returned.
        """
        return NotImplementedError
