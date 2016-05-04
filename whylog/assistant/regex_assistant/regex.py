"""
Regex verification and creating (but not finding groups in regex)
"""

import re
from collections import deque

from whylog.assistant.regex_assistant.exceptions import NotMatchingRegexError
from whylog.assistant.span import Span
from whylog.assistant.span_list import SpanList

special_characters = frozenset('.^$*+{}?[]|()]')
group_pattern = re.compile(r"[a-zA-Z]+|[0-9]+|\s+|[\W]+")


def group_spans_from_regex(regex, text):
    """
    Creates spans from regex groups in regex corresponding to text.

    Assumption: regex matches text.
    """

    if len(regex) < 2:
        return []

    verify_regex(regex, text)

    matcher = re.match(re.compile(regex), text)
    groups_count = len(matcher.groups())
    group_ranges_in_text = [matcher.span(group_no + 1) for group_no in range(groups_count)]
    group_ranges_in_text = [(start, end) for start, end in group_ranges_in_text]

    group_ranges_in_regex = []
    parenthesis_stack = deque()
    for pos in range(1, len(regex)):
        if not regex[pos - 1] == '\\':
            if regex[pos] == '(':
                parenthesis_stack.append(pos)
            elif regex[pos] == ')':
                group_ranges_in_regex.append((parenthesis_stack.pop(), pos))

    group_ranges_in_regex.sort()
    group_regexes = [regex[start + 1:end] for start, end in group_ranges_in_regex]
    group_spans = [
        Span(
            start, end, pattern=group_regex
        ) for (start, end), group_regex in zip(group_ranges_in_text, group_regexes)
    ]
    return SpanList(group_spans).sort_by_start_and_end()


def regex_from_group_spans(group_spans, line_text):
    sorted_group_spans = group_spans.sort_by_start_and_end()
    # TODO:
    # [(1,5), (2, 3)] -> [(1,5)]
    # [(1,5), (3, 7)] -> Error somewhere
    greedy_group_spans = SpanList.not_overlapping_spans(sorted_group_spans)
    complement_spans = greedy_group_spans.complementary_spans(
        0, len(line_text), create_obvious_regex
    )
    line_spans = (complement_spans + greedy_group_spans).sort_by_start_and_end()

    regex = r""
    for span in line_spans:
        span.update_pattern(line_text)
        span_pattern = span.pattern
        if span.is_param:
            span_pattern = "(" + span_pattern + ")"
        regex += span_pattern
    regex = "^" + regex + "$"
    return regex


def verify_regex(regex, text):
    """
    Verifies regex properties such as:
    - matching a whole text
    If properties are not met, exception is raised.
    """

    # regex must match a whole text from its beginning to end.
    matcher = re.match('^%s$' % (regex,), text)

    if matcher is None:
        raise NotMatchingRegexError(text, regex)


def regex_groups(regex, text):
    matcher = re.match('^%s$' % (regex,), text)
    if matcher is None:
        raise NotMatchingRegexError(text, regex)
    else:
        return matcher.groups()


def create_obvious_regex(text):
    """
    Creates regex form text by simple transformation:
    - backslash before backslash
    - backslash before special character
    :param text: must be a raw string
    :return: obvious regex
    """
    double_backslashed_text = text.replace("\\", "\\\\")
    regex = r""
    for char in double_backslashed_text:
        if char in special_characters:
            regex += "\\"
        regex += char
    return regex


def create_date_regex(date_text):
    """
    Creates date regex based on observation that numbers in date
    are represented as 1, 2 or 4 -digit numbers
    i.e guess_date_regex("23/March/2016") = [0-9]{1,2}/[a-zA-Z]+/[0-9]{4}
    :param date_text: must be a raw string
    :return: date regex
    """
    # We divide date_text into groups consisting of:
    # only alpha or only num or only non-alphanumerical marks
    date_regex = r""
    for matcher in group_pattern.finditer(date_text):
        start, end = matcher.span(0)
        char = date_text[start]
        if char.isalpha():
            date_regex += "[a-zA-Z]+"
        elif char.isdigit():
            length = matcher.end(0) - matcher.start(0)
            repetition_count = "+"
            if length <= 2:
                repetition_count = "{1,2}"
            elif length == 4:
                repetition_count = "{4}"
            date_regex += "[0-9]" + repetition_count
        else:
            date_regex += create_obvious_regex(matcher.group(0))
    return date_regex


def create_matching_everything_regex(date_text):
    return r".*"
