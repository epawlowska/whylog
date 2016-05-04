import os
from unittest import TestCase

from whylog.assistant.pattern_match import ParamGroup
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.config import YamlConfig
from whylog.constraints import IdenticalConstraint
from whylog.front.utils import FrontInput
from whylog.teacher import Teacher
from whylog.teacher.user_intent import UserConstraintIntent, UserParserIntent, UserRuleIntent
from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_teacher', 'test_files']


class TestBasic(TestCase):
    def setUp(self):
        test_files_dir = 'empty_config_files'
        path = os.path.join(*path_test_files + [test_files_dir])
        parsers_path, rules_path, log_types_path = ConfigPathFactory.get_path_to_config_files(
            path, False
        )

        self.test_files = [parsers_path, rules_path, log_types_path]
        self._clean_test_files()

        yaml_config = YamlConfig(parsers_path, rules_path, log_types_path)
        regex_assistant = RegexAssistant()
        self.teacher = Teacher(yaml_config, regex_assistant)

        line_content = r'2015-12-03 12:11:00 Data is missing on comp21'
        line_source = None
        offset = 42
        self.effect_front_input = FrontInput(offset, line_content, line_source)
        self.effect_id = 0
        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)

        cause_line_content = r'2015-12-03 12:10:55 Data migration to comp21 failed'
        cause_line_source = None
        cause_offset = 55
        self.cause_front_input = FrontInput(cause_offset, cause_line_content, cause_line_source)
        self.cause_id = 1
        self.teacher.add_line(self.cause_id, self.cause_front_input)

    def tearDown(self):
        self._clean_test_files()

    def _clean_test_files(self):
        for test_file in self.test_files:
            open(test_file, 'w').close()

    def test_default_user_parser(self):
        user_rule = self.teacher.get_rule()
        effect_parser = user_rule.parsers[self.effect_id]

        wanted_effect_parser = UserParserIntent(
            'regex_assistant',
            'data_is_missing_on',
            r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data is missing on comp21$',
            None,
            [1],
            {
                1: ParamGroup(
                    content='2015-12-03 12:11:00',
                    converter='to_date'
                )
            },
            self.effect_front_input.line_content,
            self.effect_front_input.offset,
            self.effect_front_input.line_source,
        )

        assert wanted_effect_parser == effect_parser

    def test_register_remove_constraint(self):
        user_rule = self.teacher.get_rule()
        assert not user_rule.constraints

        new_effect_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data is missing on (.*)$'
        new_cause_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data migration to (.*) failed$'
        self.teacher.update_pattern(self.effect_id, new_effect_pattern)
        self.teacher.update_pattern(self.cause_id, new_cause_pattern)

        constraint_id = 1
        groups = [(self.effect_id, 2), (self.cause_id, 2)]
        constraint = IdenticalConstraint(groups=groups)
        self.teacher.register_constraint(constraint_id, constraint)
        user_rule = self.teacher.get_rule()

        wanted_constraint = UserConstraintIntent(IdenticalConstraint.TYPE, groups)
        assert wanted_constraint == user_rule.constraints[0]
        assert self.teacher._constraint_base
        assert self.teacher._constraint_links

        self.teacher.remove_constraint(constraint_id)
        user_rule = self.teacher.get_rule()
        assert not user_rule.constraints
        assert not self.teacher._constraint_base
        assert not self.teacher._constraint_links




