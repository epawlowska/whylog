from abc import ABCMeta, abstractmethod, abstractproperty

import six

from whylog.constraints.const import ConstraintType
from whylog.constraints.exceptions import (
    ConstructorGroupsCountError, ConstructorParamsError, VerificatedParamsError
)
from whylog.teacher.user_intent import UserConstraintIntent


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    """
    :param MIN_GROUPS_COUNT: minimal groups count needed to create constraint
    :param MAX_GROUPS_COUNT: maximal groups count needed to create constraint
    """

    @abstractproperty
    def TYPE(self):
        raise NotImplementedError

    @abstractproperty
    def MIN_GROUPS_COUNT(self):
        raise NotImplementedError

    @abstractproperty
    def MAX_GROUPS_COUNT(self):
        raise NotImplementedError

    @abstractproperty
    def PARAMS(self):
        raise NotImplementedError

    @abstractmethod
    def __init__(self, groups, param_dict=None):
        """
        For Teacher and Front use while creating user rule.

        :param param_dict: dict of additional params of constraint
        :param groups: all groups that are linked by constraint,
                       represented by list of tuples (line_id, group_no),
                       where line_id and group_no is inner numeration between Front and Teacher
        """
        self.params = param_dict or {}
        self.groups = groups
        self._check_constructor_groups()
        self._check_constructor_params()

    def _check_constructor_groups(self):
        groups_count = len(self.groups)
        if (self.MIN_GROUPS_COUNT is not None and groups_count < self.MIN_GROUPS_COUNT)\
                or (self.MAX_GROUPS_COUNT is not None and groups_count > self.MAX_GROUPS_COUNT):
            raise ConstructorGroupsCountError(
                self.TYPE, len(self.groups), self.MIN_GROUPS_COUNT, self.MAX_GROUPS_COUNT
            )

    @abstractmethod
    def _check_constructor_params(self):
        pass

    def convert_to_user_constraint_intent(self):
        """
        Converts constraint to UserConstraintIntent object.

        For Teacher and Config use while saving constraint into Whylog knowledge base.
        """
        return UserConstraintIntent(self.TYPE, self.groups, self.params)

    @classmethod
    def get_param_names(cls):
        """
        Returns names of constraint additional params.

        For Front to display param names to user and then ask user for param contents.
        """
        return cls.PARAMS

    @classmethod
    def get_groups_count(cls):
        """
        Returns minimal and maximal count of groups needed to create constraint.

        For Front to ask user for proper count of groups.
        2, None - at least 2 groups
        2, 2 - exactly 2 groups
        """
        return cls.MIN_GROUPS_COUNT, cls.MAX_GROUPS_COUNT

    def verify(cls, group_contents, param_dict):
        """
        Verifies constraint for given params in param_dict and groups contents.

        :param param_dict: dict of additional params of constraint
        :param groups: list of groups contents,

        For LogReader and Teacher verification.
        It must be optimized as well as possible (for LogReader).
        """

        pass


class TimeConstraint(AbstractConstraint):
    """
    Time delta between two dates must be greater than 'max_delta' and lower than 'min_delta'
    """

    TYPE = ConstraintType.TIME_DELTA

    MIN_GROUPS_COUNT = 2
    MAX_GROUPS_COUNT = 2

    MIN_DELTA = 'min_delta'
    MAX_DELTA = 'max_delta'

    PARAMS = sorted([MIN_DELTA, MAX_DELTA])

    def __init__(self, groups, param_dict):
        """
        :param groups: First element of groups is a group with earlier date.

        I.e:
        TimeConstraint(
            [(0, 1), (2, 1)]
            {'min_delta': datetime.timedelta(seconds=1), 'max_delta': datetime.timedelta(seconds=10)},
        )
        """
        super(TimeConstraint, self).__init__(groups, param_dict)

    def _check_constructor_params(self):
        param_names = set(self.params.keys())
        correct_param_names = set(self.get_param_names())
        if (self.MIN_DELTA not in param_names and self.MAX_DELTA not in param_names)\
                or param_names - correct_param_names:
            raise ConstructorParamsError(self.TYPE, correct_param_names, param_names)

    @classmethod
    def verify(cls, group_contents, param_dict):
        lower_date, greater_date = group_contents
        actual_delta = greater_date - lower_date
        param_min_delta = param_dict[cls.MIN_DELTA]
        param_max_delta = param_dict[cls.MAX_DELTA]
        if param_min_delta is not None and actual_delta < param_min_delta:
            return False
        if param_max_delta is not None and actual_delta > param_max_delta:
            return False
        return True


class IdenticalConstraint(AbstractConstraint):
    """
    Contents of groups must be identical.
    """

    TYPE = ConstraintType.IDENTICAL

    MIN_GROUPS_COUNT = 2
    MAX_GROUPS_COUNT = None

    PARAMS = []

    def __init__(self, groups, param_dict=None):
        """
        I.e:
        IdenticalConstraint(
            [(1, 2), (2, 4)]
        )
        """
        super(IdenticalConstraint, self).__init__(groups, param_dict)

    def _check_constructor_params(self):
        if self.params:
            raise ConstructorParamsError(self.TYPE, self.get_param_names(), self.params.keys())

    @classmethod
    def verify(cls, group_contents, param_dict=None):
        """
        I.e:
        - verify({}, ['comp1', 'comp1', 'comp1']) returns True
        - verify({}, ['comp1', 'hello', 'comp1']) returns False
        """
        if len(group_contents) < 2:
            raise VerificatedParamsError(cls.TYPE, group_contents)
        first_group_content = group_contents[0]
        for group_content in group_contents:
            if not first_group_content == group_content:
                return False
        return True


class DifferentValueConstraint(AbstractConstraint):
    """
    Contents of groups must be different.
    """


class ValueDeltaConstraint(AbstractConstraint):
    """
    Value delta between values must be greater than 'min_delta' and lower than 'max_delta'
    """


class HeteroConstraint(AbstractConstraint):
    """
    A number of groups must be identical, the rest must be different.
    """
