import six

from whylog.teacher.constraint_links_base import ConstraintLinksBase
from whylog.teacher.exceptions import NotUniqueParserName
from whylog.teacher.mock_outputs import create_sample_rule
from whylog.teacher.user_intent import UserParserIntent, UserRuleIntent


class PatternGroup(object):
    """
    Keeps "coordinates" of group that represents param in text
    :param line_id: id of line to which group belongs.
    :param number: number of group in line.
                   Groups don't overlap. Numeration from left, from 1.
    """

    def __init__(self, line_id, group_number_in_line):
        self.line_id = line_id
        self.number = group_number_in_line


class TeacherParser(object):
    """
    :type line: FrontInput
    """

    def __init__(self, line_object, name, primary_keys, log_type):
        self.line = line_object
        self.name = name
        self.primary_keys = primary_keys
        self.log_type = log_type


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    :type config: AbstractConfig
    :type pattern_assistant: AbstractAssistant
    :type _parsers: dict[int, TeacherParser]
    :type _constraint_base: dict[int, AbstractConstraint]
    :param _constraint_links: Keeps links between constraints and groups.
                              Link between constraint C and group G exists
                              if C describes relation between G and other groups.
    :type _constraint_links: ConstraintLinksBase
    """

    def __init__(self, config, pattern_assistant):
        self.config = config
        self.pattern_assistant = pattern_assistant

        self._parsers = {}
        self._constraint_base = {}
        self._constraint_links = ConstraintLinksBase()
        self.effect_id = None

        self.names_blacklist = set()

    def add_line(self, line_id, line_object, effect=False):
        """
        Adds new line to rule.
        If line_id already exists, old line is overwritten by new line
        and all constraints related to old line are removed.
        """
        if line_id in six.iterkeys(self._parsers):
            self.remove_line(line_id)
        if effect:
            self.effect_id = line_id
        self._add_default_parser(line_id, line_object)

    def _add_default_parser(self, line_id, line_object):
        self.pattern_assistant.add_line(line_id, line_object)

        default_pattern_match = self.pattern_assistant.get_pattern_match(line_id)
        default_pattern = default_pattern_match.pattern
        default_groups = default_pattern_match.param_groups

        default_name = self.config.propose_parser_name(
            line_object.line_content, default_pattern, self.names_blacklist
        )
        defaulf_primary_key = [min(default_groups.keys())] if default_groups else []
        default_log_type_name = None  #TODO: What should be default log_type_name?

        new_teacher_parser = TeacherParser(
            line_object, default_name, defaulf_primary_key, default_log_type_name
        )
        self._parsers[line_id] = new_teacher_parser

        self.names_blacklist.add(default_name)

    def remove_line(self, line_id):
        """
        Removes line from rule.
        Assumption: line with line_id exists in rule.
        Removes also all constraints related to this line.
        TODO: Update related constraints rather than remove.
        """

        self._remove_constraints_by_line(line_id)
        self.pattern_assistant.remove_line(line_id)
        self.names_blacklist.remove(self._parsers[line_id].name)
        del self._parsers[line_id]

    def update_pattern(self, line_id, pattern):
        """
        Loads text pattern proposed by user, verifies if it matches line text.
        Removes constraints related with updating line
        TODO: Update related constraints rather than remove.
        """
        self.pattern_assistant.update_by_pattern(line_id, pattern)
        self._remove_constraints_by_line(line_id)

    def guess_patterns(self, line_id):
        """
        Returns list of guessed patterns for a line.
        """
        pattern_matches = self.pattern_assistant.guess_pattern_matches(line_id)
        return [pattern_match.pattern for pattern_match in pattern_matches]

    def choose_guessed_pattern(self, line_id, pattern_id):
        self.pattern_assistant.update_by_guessed_pattern_match(line_id, pattern_id)

    def set_pattern_name(self, line_id, name):
        if self.config.is_free_parser_name(name, self.names_blacklist):
            self._parsers[line_id].name = name
            self.names_blacklist.add(name)
        else:
            raise NotUniqueParserName(name)

    def set_converter(self, line_id, group_no, converter):
        # TODO: validate converter
        self.pattern_assistant.set_converter(line_id, group_no, converter)

    def set_primary_key(self, line_id, group_numbers):
        # TODO: validate primary_key
        self._parsers[line_id].primary_keys = group_numbers

    def set_log_type(self, line_id, log_type):
        pass

    def register_constraint(self, constraint_id, constraint):
        """
        Adds new constraint to rule.
        If constraint_id already exists, constraint with this constraint_id
        is overwritten by new constraint
        :param pattern_groups: groups in pattern that are linked by constraint
        :type pattern_groups: list[PatternGroup]
        """
        if constraint_id in six.iterkeys(self._constraint_base):
            self.remove_constraint(constraint_id)

        self._constraint_base[constraint_id] = constraint
        new_constraint_links = [
            (line_id, group_no, constraint_id) for (line_id, group_no) in constraint.groups
        ]
        self._constraint_links.add_links(new_constraint_links)

    def remove_constraint(self, constraint_id):
        """
        Removes constraint from rule.
        Assumption: Constraint already exists in rule.
        """
        self._constraint_links.remove_links_by_constraint(constraint_id)
        del self._constraint_base[constraint_id]

    def _remove_constraints_by_line(self, line_id):
        constraints_to_remove = self._constraint_links.remove_links_by_line(line_id)
        for constraint_id in constraints_to_remove:
            self.remove_constraint(constraint_id)

    def _remove_constraint_by_group(self, group):
        constraints_to_remove = self._constraint_links.remove_links_by_group(
            group.line_id, group.number
        )
        for constraint_id in constraints_to_remove:
            self.remove_constraint(constraint_id)

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
        """
        pass

    def make_group(self, line_id, span):
        """
        Improves text pattern by adding group corresponding to param in text.
        Removes (or maybe updates) constraints related to groups in line with line_id
        """
        pass

    def remove_group(self, pattern_group):
        """
        Improves text pattern by removing group corresponding to param in text.
        Removes (or maybe updates) constraints related to groups in line with line_id
        """
        pass

    def _verify(self):
        """
        Verifies if text patterns and constraints meet all requirements.
        E.g it is required text pattern match its line in one way only.
        """
        pass

    def test_rule(self):
        """
        Simulates searching causes with alreday created rule.
        """
        pass

    def _prepare_user_parser(self, line_id):
        """
        :type pattern_match: PatternMatch
        """
        pattern_match = self.pattern_assistant.get_pattern_match(line_id)
        teacher_parser = self._parsers[line_id]
        pattern_type = self.pattern_assistant.TYPE
        return UserParserIntent(
            pattern_type, teacher_parser.name, pattern_match.pattern, teacher_parser.log_type,
            teacher_parser.primary_keys, pattern_match.param_groups,
            teacher_parser.line.line_content, teacher_parser.line.offset,
            teacher_parser.line.line_source
        )

    def get_rule(self):
        """
        Creates rule for Front that will be shown to user
        """
        user_parsers = dict(
            [
                (line_id, self._prepare_user_parser(line_id)) for line_id in self._parsers.keys()
            ]
        )
        user_constraints = [
            constraint.convert_to_user_constraint_intent()
            for constraint in self._constraint_base.values()
        ]
        return UserRuleIntent(self.effect_id, user_parsers, user_constraints)

    def save(self):
        """
        Verifies text patterns and constraints. If they meet all requirements, saves Rule.
        """
        # TODO: remove mock
        self.config.add_rule(self.get_rule())
