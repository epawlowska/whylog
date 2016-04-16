from abc import ABCMeta, abstractmethod

import six

from whylog.constraints.const import ConstraintType
from whylog.constraints.exceptions import ConstraintVerificationError, ConstructorParamsError
from whylog.teacher.user_intent import UserConstraintIntent


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    type = 'undefined'

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
        return UserConstraintIntent(self.type, self.groups, self.params)

    @classmethod
    def get_param_names(cls):
        """
        Returns names of constraint additional params.

        For Front to display param names to user and then ask user for param contents.
        """
        raise NotImplementedError("Subclass should implement this")

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

    type = ConstraintType.TIME_DELTA

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
    def verify(cls, param_dict, group_contents):
        #TODO
        raise NotImplementedError


class IdenticalConstraint(AbstractConstraint):
    """
    Contents of groups must be identical.
    """

    type = ConstraintType.IDENTICAL

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
    def verify(cls, param_dict, group_contents):
        """
        I.e:
        - verify({}, ['comp1', 'comp1', 'comp1']) should pass
        - verify({}, ['comp1', 'hello', 'comp1']) should raise error
        """
        if not len(set(group_contents)) == 1:
            raise ConstraintVerificationError(cls.type, param_dict, group_contents)


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
