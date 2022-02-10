"""
Manage handling of affected files
"""

from my_env import data_file


def _load_from_w(file_name):
    with data_file(file_name + '.pyon') as file:
        # pylint: disable=eval-used
        return eval(file.read())


class _Extension:
    @property
    def options(self):
        """
        :return: extension options dictionary (size: count)
        """
        return self._joined

    def names(self):
        """
        :return: list of extension names
        """
        return self._names

    def __init__(self, names, histogram):
        self._joined = self._join(names, histogram)
        self._names = names

    @staticmethod
    def _join(names, histogram):
        joined = {}
        for name in names:
            for size, count in histogram[name].items():
                if size <= 0:
                    continue
                if size not in joined:
                    joined[size] = 0
                joined[size] += count
        return joined


# pylint: disable=too-few-public-methods
class Index:
    """
    Affected file index, buy extension and size
    """
    @property
    def total_size(self):
        """
        :return: (int) total size, in bytes, of all affected files
        """
        return self._total_size

    def __init__(self):
        self._options, self._total_size = self._make_options_and_sum()

    def get_matches(self, extension_name, size):
        """
        Get matches for extension and size
        :param extension_name: candidate extension
        :param size: candidate size
        :return: (int, string):
                optional-match count, '|' joined extension names (on None if extension is unknown)
        """
        low = extension_name.lower()
        extension = self._options[low] if low in self._options else None
        extension_options = extension.options() if extension else {}
        return (extension_options[size], extension.names) if size in extension_options else (0, [])

    @staticmethod
    def _make_options_and_sum():
        # dictionary of extension.lower() to array of orig_extension
        ext_names = _load_from_w('ext_vers')
        # dictionary orig_extension to [dictionary of actual-size to count]
        #  (size special cases: -1 to minimal size, 0 to maximal size)]
        histogram = _load_from_w('ext_histogram')
        total_size = sum(v[0]*v[1] for e in histogram.values() for v in e.items() if v[0] > 0)
        return {low: _Extension(names, histogram) for low, names in ext_names.items()}, total_size
