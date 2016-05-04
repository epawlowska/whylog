import os
from unittest import TestCase

from whylog.assistant.pattern_match import ParamGroup
from whylog.assistant.regex_assistant import RegexAssistant
from whylog.config import YamlConfig
from whylog.front.utils import FrontInput
from whylog.teacher import Teacher
from whylog.teacher.user_intent import UserParserIntent, UserRuleIntent
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

    def tearDown(self):
        self._clean_test_files()

    def _clean_test_files(self):
        for test_file in self.test_files:
            open(test_file, 'w').close()

    def test_prepare_user_rule(self):
        line_content = r'2015-12-03 12:11:00 Data is missing on comp21'
        line_source = None
        offset = 42
        front_input = FrontInput(offset, line_content, line_source)

        line_id = 0
        self.teacher.add_line(line_id, front_input, effect=True)

        user_rule = self.teacher.get_rule()

        wanted_parser = UserParserIntent(
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
            line_content,
            offset,
            line_source,
        )

        wanted_rule = UserRuleIntent(line_id, parsers={line_id: wanted_parser})
        assert user_rule == wanted_rule
