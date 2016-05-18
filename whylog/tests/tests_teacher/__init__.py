import os
from unittest import TestCase

import six

from whylog.assistant.pattern_match import ParamGroup
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.assistant.regex_assistant.regex import create_obvious_regex
from whylog.assistant.validation_problems import NotMatchingPatternProblem, WrongConverterProblem
from whylog.config import YamlConfig
from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.investigation_plan import LineSource
from whylog.config.log_type import LogType
from whylog.constraints import IdenticalConstraint
from whylog.converters import ConverterType
from whylog.front.utils import FrontInput
from whylog.teacher import Teacher
from whylog.teacher.user_intent import UserConstraintIntent, UserParserIntent
from whylog.teacher.rule_validation_problems import NotUniqueParserNameProblem, WrongPrimaryKeyProblem, WrongLogTypeProblem, ValidationResult
from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_teacher', 'test_files']


class TestBase(TestCase):
    def setUp(self):
        """
        Creates teacher with sample Rule.
        """
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
        self._add_test_rule()

    def _add_test_rule(self):
        """
        Adds Rule with no constraints.
        """
        line_content = r'2015-12-03 12:11:00 Error occurred in reading test'
        line_source = LineSource('sample_host', 'sample_path')
        offset = 42
        self.effect_front_input = FrontInput(offset, line_content, line_source)
        self.effect_id = 0
        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)

        cause1_line_content = r'2015-12-03 12:10:55 Data is missing on comp21'
        cause1_line_source = LineSource('sample_host1', 'sample_path1')
        cause1_offset = 30
        cause1_front_input = FrontInput(cause1_offset, cause1_line_content, cause1_line_source)
        self.cause1_id = 1
        self.teacher.add_line(self.cause1_id, cause1_front_input)
        self.cause1_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data is missing on (.*)$'
        self.teacher.update_pattern(self.cause1_id, self.cause1_pattern)

        cause2_line_content = r'2015-12-03 12:10:50 Data migration to comp21 failed in test 123'
        cause2_line_source = LineSource('sample_host2', 'sample_path2')
        cause2_offset = 21
        cause2_front_input = FrontInput(cause2_offset, cause2_line_content, cause2_line_source)
        self.cause2_id = 2
        self.teacher.add_line(self.cause2_id, cause2_front_input)
        cause2_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Data migration to (.*) failed in test (.*)$'
        self.teacher.update_pattern(self.cause2_id, cause2_pattern)

        self.identical_groups = [(self.cause1_id, 2), (self.cause2_id, 2)]

    def tearDown(self):
        self._clean_test_files()

    def _clean_test_files(self):
        for test_file in self.test_files:
            open(test_file, 'w').close()


class TestParser(TestBase):
    def _initial_validation_check(self):
        validation_result = self.teacher.validate()
        assert not validation_result.warnings
        assert len(validation_result.errors) == 3
        assert WrongLogTypeProblem(self.effect_id) in validation_result.errors
        assert WrongLogTypeProblem(self.cause1_id) in validation_result.errors
        assert WrongLogTypeProblem(self.cause2_id) in validation_result.errors

    def test_default_user_parser(self):
        self._initial_validation_check()

        user_rule = self.teacher.get_rule()
        effect_parser = user_rule.parsers[self.effect_id]
        wanted_effect_parser = UserParserIntent(
            'regex_assistant',
            'error_occurred_in_reading',
            r'([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Error occurred in reading test$',
            None,
            [1],
            {
                1: ParamGroup(
                    content='2015-12-03 12:11:00',
                    converter=ConverterType.TO_DATE
                )
            },
            self.effect_front_input.line_content,
            self.effect_front_input.offset,
            self.effect_front_input.line_source,
        )  # yapf: disable
        assert wanted_effect_parser == effect_parser

    def test_setting_parser_name(self):
        effect_parser_name = self.teacher.get_rule().parsers[self.effect_id].pattern_name
        new_name = effect_parser_name + '_hello'
        self.teacher.set_pattern_name(self.effect_id, new_name)
        rule = self.teacher.get_rule()
        assert new_name == rule.parsers[self.effect_id].pattern_name

        self._initial_validation_check()

    def test_setting_wrong_parser_name(self):
        effect_parser_name = self.teacher.get_rule().parsers[self.effect_id].pattern_name
        self.teacher.set_pattern_name(self.cause1_id, effect_parser_name)
        rule = self.teacher.get_rule()
        assert effect_parser_name == rule.parsers[self.cause1_id].pattern_name

        validation_result = self.teacher.validate()
        effect_name_problem = NotUniqueParserNameProblem(self.cause1_id)
        cause1_name_problem = NotUniqueParserNameProblem(self.effect_id)
        assert effect_name_problem in validation_result.errors
        assert cause1_name_problem in validation_result.errors

    def test_setting_converter(self):
        parser = self.teacher.get_rule().parsers[self.cause2_id]
        new_converter = ConverterType.TO_FLOAT
        assert not new_converter == parser.groups[3].converter

        self.teacher.set_converter(self.cause2_id, 3, new_converter)
        parser = self.teacher.get_rule().parsers[self.cause2_id]
        assert new_converter == parser.groups[3].converter

        self._initial_validation_check()

    def test_setting_wrong_converter(self):
        parser = self.teacher.get_rule().parsers[self.effect_id]
        wrong_converter = ConverterType.TO_FLOAT
        date_group_no = 1
        assert not wrong_converter == parser.groups[date_group_no].converter

        self.teacher.set_converter(self.effect_id, date_group_no, wrong_converter)
        parser = self.teacher.get_rule().parsers[self.effect_id]
        assert wrong_converter == parser.groups[date_group_no].converter

        validation_result = self.teacher.validate()
        converter_problem = WrongConverterProblem(
            parser.groups[date_group_no].content, parser.groups[date_group_no].converter,
            self.effect_id
        )
        assert converter_problem in validation_result.errors

    def test_setting_primary_key(self):
        parser = self.teacher.get_rule().parsers[self.cause1_id]
        new_primary_key_groups = [1, 2]
        assert not new_primary_key_groups == parser.primary_key_groups
        self.teacher.set_primary_key(self.cause1_id, new_primary_key_groups)
        parser = self.teacher.get_rule().parsers[self.cause1_id]
        assert new_primary_key_groups == parser.primary_key_groups

    def test_setting_wrong_primary_key(self):
        wrong_primary_key_groups = [1, 30000]
        self.teacher.set_primary_key(self.effect_id, wrong_primary_key_groups)
        parser = self.teacher.get_rule().parsers[self.effect_id]
        assert wrong_primary_key_groups == parser.primary_key_groups

        validation_result = self.teacher.validate()
        primary_key_problem = WrongPrimaryKeyProblem(
            wrong_primary_key_groups, parser.groups.keys(), self.effect_id
        )
        assert primary_key_problem in validation_result.errors

    def test_setting_log_type(self):
        #TODO setting simple RegexSuperParser
        sample_filename_matcher = WildCardFilenameMatcher(
            'localhost', 'sample_path', 'default', None
        )
        new_log_type = LogType('localhost', [sample_filename_matcher])
        self.teacher.set_log_type(self.effect_id, new_log_type)
        parser = self.teacher.get_rule().parsers[self.effect_id]
        assert new_log_type == parser.log_type_name

    def test_update_pattern(self):
        new_effect_pattern = r'^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}) Error occurred in (.*) test$'
        self.teacher.update_pattern(self.effect_id, new_effect_pattern)
        updated_pattern = self.teacher.get_rule().parsers[self.effect_id].pattern
        assert new_effect_pattern == updated_pattern
        groups = self.teacher.get_rule().parsers[self.effect_id].groups
        assert len(groups) == 2

        self._initial_validation_check()

    def test_update_not_matching_pattern(self):
        not_matching_pattern = 'foo bar (.*) Bar$'
        self.teacher.update_pattern(self.effect_id, not_matching_pattern)

        updated_pattern = self.teacher.get_rule().parsers[self.effect_id].pattern
        assert not_matching_pattern == updated_pattern

        groups = self.teacher.get_rule().parsers[self.effect_id].groups
        assert not groups

        validation_result = self.teacher.validate()
        problem = NotMatchingPatternProblem(self.effect_id)
        assert problem in validation_result.warnings

    def test_guess_patterns(self):
        effect_guessed_patterns = self.teacher.guess_patterns(self.effect_id)
        assert len(effect_guessed_patterns) > 1
        effect_guessed_regexes = [
            pattern_match.pattern for pattern_match in six.itervalues(effect_guessed_patterns)
        ]
        effect_obvious_regex = create_obvious_regex(self.effect_front_input.line_content)
        assert effect_obvious_regex in effect_guessed_regexes


class TestConstraints(TestBase):
    def _register_identical_constraint(self, constraint_id=1):
        constraint = IdenticalConstraint(groups=self.identical_groups)
        self.teacher.register_constraint(constraint_id, constraint)

    def _constraints_absence_check(self):
        user_rule = self.teacher.get_rule()
        assert not user_rule.constraints
        assert not self.teacher._constraint_base
        assert not self.teacher._constraint_links.get_links()

    def _constraints_presence_check(self):
        user_rule = self.teacher.get_rule()
        assert user_rule.constraints
        assert self.teacher._constraint_base
        assert self.teacher._constraint_links.get_links()

    def test_register_and_remove_constraint(self):
        self._constraints_absence_check()

        constraint_id = 1
        constraint = IdenticalConstraint(groups=self.identical_groups)
        self.teacher.register_constraint(constraint_id, constraint)
        user_rule = self.teacher.get_rule()

        wanted_constraint = UserConstraintIntent(IdenticalConstraint.TYPE, self.identical_groups)
        assert wanted_constraint == user_rule.constraints[0]

        self._constraints_presence_check()

        self.teacher.remove_constraint(constraint_id)

        self._constraints_absence_check()

    def test_remove_line(self):
        """
        Removing line should indicate removal of related constraints.
        """
        self._register_identical_constraint()

        self._constraints_presence_check()

        self.teacher.remove_line(self.cause1_id)

        self._constraints_absence_check()

    def test_update_pattern(self):
        """
        Updating pattern of line should indicate removal of related constraints.
        (even if new pattern is the same as old or has the same groups)
        """
        self._register_identical_constraint()

        self._constraints_presence_check()

        self.teacher.update_pattern(self.cause1_id, self.cause1_pattern)

        self._constraints_absence_check()
