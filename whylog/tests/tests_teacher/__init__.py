import os

from unittest import TestCase

from whylog.teacher import Teacher
from whylog.config import YamlConfig
from whylog.assistant.regex_assistant import RegexAssistant

from whylog.tests.utils import ConfigPathFactory

path_test_files = ['whylog', 'tests', 'tests_teacher', 'test_files']


class TestPrivateMethods(TestCase):
    def setUp(self):
        path = os.path.join(*path_test_files)
        parsers_path, rules_path, log_types_path = ConfigPathFactory.get_path_to_config_files(
            path, False
        )
        yaml_config = YamlConfig(parsers_path, rules_path, log_types_path)
        regex_assistant = RegexAssistant()
        self.teacher = Teacher(yaml_config, regex_assistant)

    def test_prepare_user_parser(self):
        pass

