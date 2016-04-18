from unittest import TestCase

from whylog.constraints import IdenticalConstraint
from whylog.constraints.exceptions import ConstraintVerificationError


class TestIdenticalConstraint(TestCase):
    def test_get_param_names(self):
        assert IdenticalConstraint.get_param_names() == []

    def test_get_group_count(self):
        assert IdenticalConstraint.get_groups_count() == (2, None)

    def test_verify_success(self):
        assert IdenticalConstraint.verify({}, ['comp1', 'comp1', 'comp1'])

    def test_verify_fail(self):
        assert not IdenticalConstraint.verify({}, ['comp1', 'hello', 'comp1'])
