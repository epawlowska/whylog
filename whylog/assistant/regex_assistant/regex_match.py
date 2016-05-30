import six

from whylog.assistant.pattern_match import ParamGroup, PatternMatch
from whylog.assistant.regex_assistant.guessing import guess_pattern_match
from whylog.assistant.regex_assistant.regex import NotMatchingRegexError, regex_groups, verify_regex
from whylog.converters import ConverterType
from whylog.assistant.validation_problems import NotMatchingPatternProblem


class RegexMatch(object):
    """
    Container for information about line and corresponding regex
    Keeps own data integrity - especially consistency between regex and groups (param_groups).
    Verifies updates.

    :param line_text: raw string of the line
    :param param_groups: represents params from text (catched by regex groups)
    :param regex: regex matching to line_text
    :param guessed_pattern_matches: keeps guessed regexes that match to line_text
    :type param_groups: dict[int, ParamGroup]
    :type guessed_pattern_matches: dict[int, PatternMatch]
    """

    def __init__(self, line_object):
        self.line_text = line_object.line_content
        self.param_groups = dict()

        self.regex = None
        self.primary_key = None

        self.guessed_pattern_matches = dict()

        self._guess_regexes()
        self.update_by_guessed_regex(0)

    def convert_to_pattern_match(self):
        return PatternMatch(self.line_text, self.regex, self.param_groups, self.primary_key)

    def update_by_regex(self, new_regex):
        """
        Assigns self.regex to new_regex.

        Throws NotMatchingRegexError if new_regex doesn't match self.line_text
        If needed, improves new_regex: new_regex = '^' + new_regex + '$' (regex must match whole line)
        Updates self.param_groups so that they correspond to new_regex groups
        """

        if new_regex[-1] != '$':
            new_regex += '$'

        try:
            verify_regex(new_regex, self.line_text)
        except NotMatchingRegexError:
            self.regex = new_regex
            self.param_groups = {}
            self.primary_key = []
            return

        groups = regex_groups(new_regex, self.line_text)
        default_converter = ConverterType.TO_STRING
        self.param_groups = dict(
            (key + 1, ParamGroup(groups[key], default_converter))
            for key in six.moves.range(len(groups))
        )
        self.regex = new_regex

    def update_by_pattern_match(self, pattern_match):
        self.update_by_regex(pattern_match.pattern)
        self.param_groups = pattern_match.param_groups
        self.primary_key = pattern_match.primary_key

    def update_by_guessed_regex(self, regex_id):
        self.update_by_pattern_match(self.guessed_pattern_matches[regex_id])

    def _guess_regexes(self):
        guessed_pattern_matches = guess_pattern_match(self.line_text)
        guessed_dict = dict(
            (key, guessed_pattern_matches[key])
            for key in six.moves.range(len(guessed_pattern_matches))
        )
        self.guessed_pattern_matches = guessed_dict

    def set_converter(self, group_no, converter):
        self.param_groups[group_no].converter = converter

    def set_primary_key(self, primary_key):
        self.primary_key = primary_key

    def _validate_pattern(self):
        try:
            verify_regex(self.regex, self.line_text)
        except NotMatchingRegexError:
            return [NotMatchingPatternProblem()]
        else:
            return []

    def validate(self):
        """
        Verifies:
        - regex matching a whole text
        - proper group converters
        - primary key is subset of group numbers
        """

        pattern_match = self.convert_to_pattern_match()
        return self._validate_pattern() + pattern_match.validate_converters() + \
               pattern_match.validate_primary_key()
