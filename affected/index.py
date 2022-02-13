"""
Manage handling of affected files
"""

from my_env import data_file


def load_pyon_data_file(file_name):
    """
    Loads encoded python object from file
    :param file_name: name of file in data folder (without extension)
    :return: evaluated pyton object
    """
    with data_file(file_name + '.pyon') as file:
        # pylint: disable=eval-used
        return eval(file.read())


class _Option:
    @property
    def count(self):
        """
        :return: number of affected files matches by this extension in all its forms
        """
        return self._count

    @property
    def names(self):
        """
        :return: list of extension names
        """
        return self._names

    def __init__(self):
        self._count = 0
        self._names = []

    def add(self, name, count):
        """
        Add name and count
        :param name: extension name
        :param count: option count
        """
        self._names.append(name)
        self._count += count


# pylint: disable=too-few-public-methods
class Index:
    """
    Affected file index, by extension and size
    """
    @property
    def total_size(self):
        """
        :return: (int) total size, in bytes, of all affected files
        """
        return self._total_size

    def __init__(self):
        # options is a dictionary of ext: (dictionary of size: _Option)
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
        options = self._options[low] if low in self._options else None
        option = options[size] if (options and size in options) else None
        return (option.count, option.names) if option else (0, [])

    @staticmethod
    def _make_options_and_sum():
        # dictionary of extension.lower() to array of orig_extension
        ext_names = load_pyon_data_file('ext_vers')
        # dictionary orig_extension to [dictionary of actual-size to count]
        #  (size special cases: -1 to minimal size, 0 to maximal size)]
        histogram = load_pyon_data_file('ext_histogram')
        total_size = sum(v[0] * v[1] for e in histogram.values() for v in e.items() if v[0] > 0)
        return {low: Index._join(names, histogram) for low, names in ext_names.items()}, total_size

    @staticmethod
    def _join(names, histogram):
        joined = {}
        for name in names:
            for size, count in histogram[name].items():
                if size <= 0:
                    continue
                if size not in joined:
                    joined[size] = _Option()
                joined[size].add(name, count)
        return joined
