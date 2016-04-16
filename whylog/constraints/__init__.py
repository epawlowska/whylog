from abc import ABCMeta, abstractmethod

import six

from whylog.constraints.const import ConstraintType
from whylog.constraints.exceptions import ConstraintVerificationError, ConstructorParamsError
from whylog.teacher.user_intent import UserConstraintIntent


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    """
    :param MIN_GROUPS_COUNT: minimal groups count needed to create constraint
    :param MAX_GROUPS_COUNT: maximal groups count needed to create constraint
    """

    TYPE = 'undefined'
    MIN_GROUPS_COUNT = None
    MAX_GROUPS_COUNT = None

    @abstractmethod
    def __init__(self, param_dict, groups):
        """
        Creates constraint object.

        For Teacher and Front use while creating user rule.

        :param param_dict: dict of additional params of constraint
        :param groups: list of tuples (line_id, group_no),
                       where line_id and group_no is inner numeration between Front and Teacher
        """
        param_dict_keys = param_dict.keys()
        correct_param_names = self.get_param_names()
        if not param_dict_keys == correct_param_names:
            raise ConstructorParamsError(correct_param_names, param_dict_keys)
        self.params = param_dict
        self.groups = groups

    @abstractmethod
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
        raise NotImplementedError("Subclass should implement this")

    @classmethod
    def get_groups_count(cls):
        """
        Returns minimal and maximal count of groups needed to create constraint.

        For Front to ask user for proper count of groups.
        0, 0 - no groups
        2, None - at least 2 groups
        2, 2 - exactly 2 groups
        """
        return cls.MIN_GROUPS_COUNT, cls.MAX_GROUPS_COUNT

    @classmethod
    def verify(cls, param_dict, group_contents):
        """
        Verifies constraint for given params and groups contents.

        For LogReader and Teacher verification.
        """
        raise NotImplementedError("Subclass should implement this")


class TimeConstraint(AbstractConstraint):
    """
    Time delta between two dates must be greater than 'max_delta' and lower than 'min_delta'
    """

    TYPE = ConstraintType.TIME_DELTA

    MIN_GROUPS_COUNT = 0
    MAX_GROUPS_COUNT = 0

    GROUP_EARLIER = 'group_earlier'
    GROUP_LATER = 'group_later'
    MIN_DELTA = 'min_delta'
    MAX_DELTA = 'max_delta'

    def __init__(self, param_dict, groups):
        """
        I.e:
        TimeConstraint(
            {'group_earlier': (3, 1), 'group_later': (4, 2), 'min_delta': 12, 'max_delta' 30},
            list()
        )
        """
        super(TimeConstraint, self).__init__(param_dict, groups)

    def convert_to_user_constraint_intent(self):
        return super(TimeConstraint, self).convert_to_user_constraint_intent()

    @classmethod
    def get_param_names(cls):
        return [cls.GROUP_EARLIER, cls.GROUP_LATER, cls.MIN_DELTA, cls.MAX_DELTA]

    @classmethod
    def get_groups_count(cls):
        return super(TimeConstraint, cls).get_groups_count()

    @classmethod
    def verify(cls, param_dict, group_contents):
        #TODO
        raise NotImplementedError


class IdenticalConstraint(AbstractConstraint):
    """
    Contents of groups must be identical.
    """

    TYPE = ConstraintType.IDENTICAL

    MIN_GROUPS_COUNT = 2
    MAX_GROUPS_COUNT = None

    def __init__(self, param_dict, groups):
        """
        I.e:
        IdenticalConstraint(
            dict(),
            [(1, 2), (2, 4)]
        )
        """
        super(IdenticalConstraint, self).__init__(param_dict, groups)

    def convert_to_user_constraint_intent(self):
        return super(IdenticalConstraint, self).convert_to_user_constraint_intent()

    @classmethod
    def get_param_names(cls):
        return []

    @classmethod
    def get_groups_count(cls):
        return super(IdenticalConstraint, cls).get_groups_count()

    @classmethod
    def verify(cls, param_dict, group_contents):
        """
        I.e:
        - verify({}, ['comp1', 'comp1', 'comp1']) should pass
        - verify({}, ['comp1', 'hello', 'comp1']) should raise error
        """
        if not len(set(group_contents)) == 1:
            raise ConstraintVerificationError(cls.TYPE, param_dict, group_contents)

    # @classmethod
    # def verify(cls, group_contents, param_dict):
    #     if len(group_contents) <= 1:
    #         return False  # FIXME raise exception?
    #     return all(group_contents[0] == group for group in group_contents)


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
