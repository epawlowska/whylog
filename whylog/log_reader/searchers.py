import os.path
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from os import SEEK_SET

import six

from whylog.config.investigation_plan import LineSource
from whylog.log_reader.const import BufsizeConsts
from whylog.log_reader.read_utils import ReadUtils


@six.add_metaclass(ABCMeta)
class AbstractSearcher(object):
    @abstractmethod
    def search(self, search_data, original_front_input):
        """
        transfer investigation to searcher
        """
        pass


class IndexSearcher(AbstractSearcher):
    def search(self, search_data, original_front_input):
        pass


class DatabaseSearcher(AbstractSearcher):
    def search(self, search_data, original_front_input):
        pass


class BacktrackSearcher(AbstractSearcher):
    def __init__(self, file_path, investigation_step, super_parser):
        self._file_path = file_path
        self._investigation_step = investigation_step
        self._super_parser = super_parser

    def _deduce_offset(self):
        """
        returns offset of the line with the specified time
        """
        for line in self._reverse_from_offset(os.path.getsize(self._file_path)):
            line_content, line_offset = line
            if self._investigation_step.is_line_in_search_range(line_content):
                return line_offset + len(line_content) + 1

    def _find_left(self, opened_file, value, super_parser):
        return ReadUtils.binary_search_left(
            opened_file, 0, ReadUtils.size_of_opened_file(opened_file), value, super_parser
        )

    def _find_right(self, opened_file, value, super_parser):
        return ReadUtils.binary_search_right(
            opened_file, 0, ReadUtils.size_of_opened_file(opened_file), value, super_parser
        )

    def _find_offsets_range(self, opened_file, search_range, super_parser):
        """
        returns a pair of offsets between whose the investigation
        in file should be provided
        """
        # TODO: run function _find_left on left bound from search_range
        # TODO: and run functions _find_right on right bound from search_range
        pass

    @classmethod
    def _merge_clues(cls, collector, clues_from_line):
        for parser_name, clue in six.iteritems(clues_from_line):
            collector[parser_name].append(clue)

    @classmethod
    def _decrease_actual_offset_properly(cls, actual_offset, drop_string):
        return actual_offset - len(drop_string) - 1

    def _reverse_from_offset(self, offset, buf_size=BufsizeConsts.STANDARD_BUF_SIZE):
        """
        a generator that returns the pairs consisting of
        lines in reverse order and offsets corresponding to them,
        beginning with the specified offset
        """
        with open(self._file_path) as fh:
            fh.seek(offset)
            total_size = remaining_size = fh.tell()
            reverse_offset = 0
            actual_offset = offset
            truncated = None
            while remaining_size > 0:
                reverse_offset = min(total_size, reverse_offset + buf_size)
                fh.seek(total_size - reverse_offset, SEEK_SET)
                buffer_ = fh.read(min(remaining_size, buf_size))
                lines = buffer_.split('\n')
                remaining_size -= buf_size
                if truncated is not None:
                    if buffer_[-1] is not '\n':
                        lines[-1] += truncated
                    else:
                        actual_offset = self._decrease_actual_offset_properly(
                            actual_offset, truncated
                        )
                        yield truncated, actual_offset
                truncated = lines[0]
                for line in reversed(lines[1:]):
                    if len(line):
                        actual_offset = self._decrease_actual_offset_properly(actual_offset, line)
                        yield line, actual_offset
            if truncated:
                actual_offset = self._decrease_actual_offset_properly(actual_offset, truncated)
                yield truncated, actual_offset

    def search(self, original_front_input):
        clues = defaultdict(list)
        if original_front_input.line_source.path == self._file_path:
            # TODO checking if host is also the same
            offset = original_front_input.offset
        else:
            offset = self._deduce_offset()
        for line, actual_offset in self._reverse_from_offset(offset):
            # TODO: remove mock
            line_source = LineSource('localhost', self._file_path)
            clues_from_line = self._investigation_step.get_clues(line, actual_offset, line_source)
            self._merge_clues(clues, clues_from_line)
        return clues
