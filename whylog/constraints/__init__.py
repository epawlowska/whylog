from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    @abstractmethod
    def save(self, rulebase_rule):
        pass


class TimeConstraint(AbstractConstraint):
    def __init__(self, time_group_earlier, time_group, min_delta=None, max_delta=None):
        pass


class IdenticalConstraint(AbstractConstraint):
    def __init__(self, groups):
        pass


class DifferentValueConstraint(AbstractConstraint):
    def __init__(self, grouops):
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

