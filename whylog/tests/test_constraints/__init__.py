from datetime import timedelta

from unittest import TestCase

from whylog.constraints import IdenticalConstraint, TimeConstraint
from whylog.constraints.exceptions import ConstructorGroupsCountError, ConstructorParamsError


class TestIdenticalConstraint(TestCase):
    def test_constructor_success(self):
        groups = [(0, 1), (2, 1), (2, 4)]
        IdenticalConstraint(groups)
        IdenticalConstraint(groups, {})

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        self.assertRaises(ConstructorGroupsCountError, IdenticalConstraint, insufficient_groups)

    def test_constructor_not_empty_params(self):
        self.assertRaises(
            ConstructorParamsError, IdenticalConstraint, [
                (0, 1), (2, 1)
            ], {'sth': 12}
        )

    def test_get_param_names(self):
        assert IdenticalConstraint.get_param_names() == []

    def test_get_group_count(self):
        assert IdenticalConstraint.get_groups_count() == (2, None)

    def test_verify_success(self):
        assert IdenticalConstraint.verify(['comp1', 'comp1', 'comp1'])

    def test_verify_fail(self):
        assert not IdenticalConstraint.verify(['comp1', 'hello', 'comp1'])


class TestTimeConstraint(TestCase):

    def setUp(self):
        self.min_delta = timedelta(seconds=1)
        self.max_delta = timedelta(seconds=10)

    def test_constructor_success(self):
        groups = [(0, 1), (2, 1)]
        params_full = {TimeConstraint.MIN_DELTA: self.min_delta, TimeConstraint.MAX_DELTA: self.max_delta}
        TimeConstraint(groups, params_full)

        params_only_min_delta = {TimeConstraint.MIN_DELTA: self.min_delta}
        TimeConstraint(groups, params_only_min_delta)

        params_only_max_delta = {TimeConstraint.MAX_DELTA: self.max_delta}
        TimeConstraint(groups, params_only_max_delta)

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        params = {TimeConstraint.MIN_DELTA: self.min_delta}
        self.assertRaises(ConstructorGroupsCountError, TimeConstraint, insufficient_groups, params)

    def test_constructor_wrong_params(self):
        groups = [(0, 1), (2, 1)]
        no_params = {}
        self.assertRaises(ConstructorParamsError, TimeConstraint, groups, no_params)

        wrong_params = {"sth": 1}
        self.assertRaises(ConstructorParamsError, TimeConstraint, groups, wrong_params)

        mixed_params = {TimeConstraint.MIN_DELTA: 33, "sth": 1}
        self.assertRaises(ConstructorParamsError, TimeConstraint, groups, mixed_params)

    def test_get_param_names(self):
        assert set(TimeConstraint.get_param_names()) == \
               set([TimeConstraint.MIN_DELTA, TimeConstraint.MAX_DELTA])

    def test_get_group_count(self):
        assert TimeConstraint.get_groups_count() == (2, 2)
