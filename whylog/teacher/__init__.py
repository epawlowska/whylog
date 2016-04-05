from whylog.teacher.mock_outputs import create_sample_rule
from whylog.teacher.user_intent import UserRuleIntent


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    """

    def __init__(self, id_to_line_dict, effect_id, config, pattern_assistant):
        self._lines = id_to_line_dict.copy()
        self.constraints = {}
        self.rule_intent = UserRuleIntent(effect_id)
        self.config = config
        self.pattern_assistant = pattern_assistant

    def add_line(self, line_id, line_object):
        self._lines[line_id] = line_object

    def remove_line(self, line_id):
        del self._lines[line_id]
        if line_id == self.effect_id:
            # TODO: do something that represents warning "No effect line, remember to add it!"
            pass

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

    def remove_group(self, line_id, group):
        #TODO implicates pattern update and constraint update/remove (hetero)?
        pass

    def guess_pattern(self, line_id):
        """
        Guess text pattern for line text.
        """
        #TODO implicate pattern update and constraint removal
        pass

    def set_convertion(self, line_id, group, conversion):
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

    def get_rule(self):
        """
        Creates rule for Front, that will be shown to user
        """
        pass

    def save(self):
        """
        Verifies text patterns and constraints. If they meet all requirements, saves Rule.
        """
        self.config.add_rule(create_sample_rule())
