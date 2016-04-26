from unittest import TestCase

from whylog.constraints import IdenticalConstraint, TimeConstraint
from whylog.constraints.exceptions import ConstructorGroupsError, ConstructorParamsError


class TestIdenticalConstraint(TestCase):
    def test_constructor_success(self):
        IdenticalConstraint(dict(), [(0, 1), (2, 1), (2, 4)])

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        self.assertRaises(ConstructorGroupsError, IdenticalConstraint, dict(), insufficient_groups)

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
        TimeConstraint(params_full, groups)

        params_only_min_delta = dict([(TimeConstraint.MIN_DELTA, 1)])
        TimeConstraint(params_only_min_delta, groups)

        params_only_max_delta = dict([(TimeConstraint.MAX_DELTA, 1)])
        TimeConstraint(params_only_max_delta, groups)

    def test_constructor_insufficient_groups(self):
        insufficient_groups = [(0, 1)]
        params = dict([(TimeConstraint.MIN_DELTA, 1)])
        self.assertRaises(ConstructorGroupsError, TimeConstraint, params, insufficient_groups)

    def test_constructor_insufficient_params(self):
        groups = [(0, 1), (2, 1)]
        insufficient_params = dict()
        self.assertRaises(ConstructorParamsError, TimeConstraint, insufficient_params, groups)

    def test_get_param_names(self):
        assert set(TimeConstraint.get_param_names()) == \
               set([TimeConstraint.MIN_DELTA, TimeConstraint.MAX_DELTA])

    def test_get_group_count(self):
        assert TimeConstraint.get_groups_count() == (2, 2)
