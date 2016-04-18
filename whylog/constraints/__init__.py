from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class AbstractConstraint(object):
    @abstractmethod
    def save(self, rulebase_rule):
        pass


class TimeConstraint(AbstractConstraint):
    def __init__(self, line_earlier, line_later, min_delta=None, max_delta=None):
        pass


class IdenticalIntervals(AbstractConstraint):
    def __init__(self, intervals):
        pass


class DifferentValueIntervals(AbstractConstraint):
    def __init__(self, intervals):
        pass


class ValueDeltaIntervals(AbstractConstraint):
    def __init__(self, interval_lower, interval_greater, min_delta=None, max_delta=None):
        """
        Sets Minimum and maximum difference between values of params (if values are numbers).
        """
        pass
