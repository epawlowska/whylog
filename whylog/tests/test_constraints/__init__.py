from unittest import TestCase

from whylog.constraints import IdenticalConstraint
from whylog.constraints.exceptions import ConstraintVerificationError


class TestIdenticalConstraint(TestCase):
    def test_verify_success(self):
        IdenticalConstraint.verify({}, ['comp1', 'comp1', 'comp1'])

    def test_verify_fail(self):
        self.assertRaises(
            ConstraintVerificationError,
            IdenticalConstraint.verify,
            {},
            ['comp1', 'hello', 'comp1'],
        )
