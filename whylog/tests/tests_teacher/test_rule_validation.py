from whylog.config.filename_matchers import WildCardFilenameMatcher
from whylog.config.log_type import LogType
from whylog.converters import ConverterType
from whylog.tests.tests_teacher import TestBase

from whylog.assistant.validation_problems import (
    InvalidPrimaryKeyProblem, NotMatchingPatternProblem, WrongConverterProblem
)
from whylog.teacher.rule_validation_problems import (  # isort:skip
    NoEffectParserProblem, NotSetLogTypeProblem, NotUniqueParserNameProblem, ParserCountProblem
)  # yapf: disable


class TestValidationBase(TestBase):
    def _in_rule_problems(self, problem):
        validation_result = self.teacher.validate()
        return problem in validation_result.rule_problems

    def _in_parser_problems(self, parser_id, problem):
        validation_result = self.teacher.validate()
        problems = validation_result.parser_problems.get(parser_id)
        if problems is None:
            return False
        return problem in problems

    def _initial_validation_check(self):
        validation_result = self.teacher.validate()
        assert not validation_result.is_acceptable()

        assert len(validation_result.rule_problems) == 1
        assert len(validation_result.parser_problems) == 1
        assert not validation_result.constraint_problems

        assert self._in_parser_problems(self.effect_id, NotSetLogTypeProblem())
        assert self._in_rule_problems(ParserCountProblem())


class TestRuleValidation(TestValidationBase):
    def test_no_effect_parser(self):
        self.teacher.remove_line(self.effect_id)
        assert self._in_rule_problems(NoEffectParserProblem())

        self.teacher.add_line(self.effect_id, self.effect_front_input, effect=True)
        assert not self._in_rule_problems(NoEffectParserProblem())

        self._initial_validation_check()

    def test_one_parser_rule(self):
        assert self._in_rule_problems(ParserCountProblem())

        self.teacher.add_line(self.cause1_id, self.cause1_front_input)

        assert not self._in_rule_problems(ParserCountProblem())

        self.teacher.remove_line(self.cause1_id)
        self._initial_validation_check()


class TestParserValidation(TestValidationBase):
    def test_not_unique_parser_name(self):
        effect_parser_name = self.teacher.get_rule().parsers[self.effect_id].pattern_name

        self.teacher.add_line(self.cause1_id, self.cause1_front_input)
        self.teacher.set_pattern_name(self.cause1_id, effect_parser_name)

        assert self._in_parser_problems(self.effect_id, NotUniqueParserNameProblem())
        assert self._in_parser_problems(self.cause1_id, NotUniqueParserNameProblem())

        self.teacher.remove_line(self.cause1_id)

        assert not self._in_parser_problems(self.effect_id, NotUniqueParserNameProblem())
        assert not self._in_parser_problems(self.cause1_id, NotUniqueParserNameProblem())
        self._initial_validation_check()

    def test_not_set_log_type(self):
        assert self._in_parser_problems(self.effect_id, NotSetLogTypeProblem())

        sample_filename_matcher = WildCardFilenameMatcher(
            'localhost', 'sample_path', 'default', None
        )
        new_log_type = LogType('localhost', [sample_filename_matcher])
        self.teacher.set_log_type(self.effect_id, new_log_type)

        assert not self._in_parser_problems(self.effect_id, NotSetLogTypeProblem())

    def test_not_matching_pattern(self):
        not_matching_pattern = 'not matching pattern'
        self.teacher.update_pattern(self.effect_id, not_matching_pattern)
        assert self._in_parser_problems(
            self.effect_id,
            NotMatchingPatternProblem()
        )

    def test_invalid_primary_key(self):
        unlikely_primary_key = [1500, 100, 900]
        self.teacher.set_primary_key(self.effect_id, unlikely_primary_key)
        parser_groups = self.teacher.get_rule().parsers[self.effect_id].groups.keys()
        assert self._in_parser_problems(
            self.effect_id,
            InvalidPrimaryKeyProblem(unlikely_primary_key, parser_groups)
        )

    def test_invalid_converter(self):
        date_group = 1
        self.teacher.set_converter(self.effect_id, date_group, ConverterType.TO_FLOAT)
        group_content = self.teacher.get_rule().parsers[self.effect_id].groups[date_group].content
        assert self._in_parser_problems(
            self.effect_id,
            WrongConverterProblem(group_content, ConverterType.TO_FLOAT)
        )
        #TODO: other string to float check
