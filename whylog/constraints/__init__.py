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
        Creates constraint generally for Teacher and Front use.

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
        return UserConstraintIntent(self.type, self.groups, self.params)

    @classmethod
    def get_param_names(cls):
        """
        Returns names of constraint params.

        This method is for Front, who displays to user param names and asks user for param contents.
        """
        raise NotImplementedError("Subclass should implement this")

    @classmethod
    def verify(cls, param_dict, group_contents):
        """
        Verifies constraint for given params and groups contents.

        """


class TimeConstraint(AbstractConstraint):
    def __init__(self, groups, param_dict):
        pass

    @classmethod
    def verify(cls, group_contents, param_dict):
        # TODO remove mock
        return True


class IdenticalConstraint(AbstractConstraint):
    def __init__(self, groups, params):
        pass

    @classmethod
    def verify(cls, group_contents, param_dict):
        if len(group_contents) <= 1:
            return False  # FIXME raise exception?
        return all(group_contents[0] == group for group in group_contents)


class DifferentValueConstraint(AbstractConstraint):
    def __init__(self, groups):
        pass


class ValueDeltaConstraint(AbstractConstraint):
    def __init__(self, group_lower, group_greater, min_delta=None, max_delta=None):
        """
        Sets Minimum and maximum difference between values of params (if values are numbers).
        """
        pass

class HeteroConstraint(AbstractConstraint):
    def __init__(self, groups, identical_groups_conut):
        pass

