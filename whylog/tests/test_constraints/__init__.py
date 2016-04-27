from unittest import TestCase

from whylog.constraints import IdenticalConstraint, TimeConstraint
from whylog.constraints.exceptions import ConstructorGroupsError, ConstructorParamsError


class TestIdenticalConstraint(TestCase):
    def test_constructor_success(self):
        groups = [(0, 1), (2, 1), (2, 4)]
        IdenticalConstraint(groups)
        IdenticalConstraint(groups, dict())

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        self.assertRaises(ConstructorGroupsError, IdenticalConstraint, insufficient_groups)

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
        assert IdenticalConstraint.verify({}, ['comp1', 'comp1', 'comp1'])

    def test_verify_fail(self):
        assert not IdenticalConstraint.verify({}, ['comp1', 'hello', 'comp1'])


class TestTimeConstraint(TestCase):
    def test_constructor_success(self):
        groups = [(0, 1), (2, 1)]
        params_full = dict([(TimeConstraint.MIN_DELTA, 1), (TimeConstraint.MAX_DELTA, 42)])
        TimeConstraint(groups, params_full)

        params_only_min_delta = dict([(TimeConstraint.MIN_DELTA, 1)])
        TimeConstraint(groups, params_only_min_delta)

        params_only_max_delta = dict([(TimeConstraint.MAX_DELTA, 1)])
        TimeConstraint(groups, params_only_max_delta)

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        params = dict([(TimeConstraint.MIN_DELTA, 1)])
        self.assertRaises(ConstructorGroupsError, TimeConstraint, insufficient_groups, params)

    def test_constructor_wrong_params(self):
        groups = [(0, 1), (2, 1)]
        no_params = dict()
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
