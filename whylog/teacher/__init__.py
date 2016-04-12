from whylog.teacher.mock_outputs import create_sample_rule
from whylog.teacher.user_intent import UserRuleIntent


class TeacherParser(object):
    def __init__(self, line_object):
        self.line = line_object
        self.pattern_name = None
        self.log_type = None
        self.primary_keys = []


class TeacherConstraint(object):
    def __init__(self):
        self.constr_type = None
        self.params = {}


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    """

    def __init__(self, config, pattern_assistant):
        self._constraints = {}  # dict of TeacherConstraint
        self._parsers = {}  # dict of TeacherParsers
        self._group_constraint_matching = []  # list of tuples (line_id, group_no, constr_id)
        self.effect_id = None

        self.config = config
        self.pattern_assistant = pattern_assistant

    def add_line(self, line_id, line_object, effect=False):
        #TODO: check for existing line_id
        if effect:
            self.effect_id = line_id
        self._parsers[line_id] = TeacherParser(line_object)
        self.pattern_assistant.add_line(line_id, line_object)

    def remove_line(self, line_id):
        #TODO check for existing line_id, prevent line_effect_id removal
        del self._parsers[line_id]
        self.pattern_assistant.remove_line(line_id)

    def update_pattern(self, line_id, proposed_pattern):
        """
        Loads text pattern proposed by user, verifies if it matches line text.
        """
        #TODO implicate pattern update and constraint removal
        pass

    def make_group(self, line_id, span):
        """
        Improves text patterns by adding to them groups corresponding to params in text.
        """
        #TODO implicate pattern update, constraint update -> groups indexing
        pass

    def remove_group(self, line_id, group_id):
        #TODO implicates pattern update and constraint update/remove (hetero)?
        pass

    def guess_pattern(self, line_id):
        """
        Guess text pattern for line text.
        """
        #TODO implicate pattern update and constraint removal
        pass

    def set_pattern_name(self, line_id, name):
        pass

    def set_converter(self, line_id, group, converter):
        pass

    def set_primary_key(self, line_id, groups):
        pass

    def set_log_type(self, line_id, log_type):
        pass

    def register_constraint(self, constr_id, constr_type, groups, params=None):
        pass

    def remove_constraint(self, constr_id):
        pass

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
        """
        pass

    def _verify(self):
        """
        Verifies if text patterns and constraints meet all requirements.
        E.g it is required text pattern match its line in one way only.
        """
        pass

    def _prepare_rule(self):
        """
        :return UserRuleIntent
        """

    def get_rule(self):
        """
        Creates rule for Front, that will be shown to user
        """
        pass

    def test_rule(self):
        pass

    def save(self):
        """
        Verifies text patterns and constraints. If they meet all requirements, saves Rule.
        """
        self.config.add_rule(create_sample_rule())
