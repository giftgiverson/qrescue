"""
Manage handling of affected files
"""

from my_env import data_file


def _load_from_w(file_name):
    with data_file(file_name + '.pyon') as file:
        # pylint: disable=eval-used
        return eval(file.read())


# extension histogram, dictionary orig_extension to [dictionary of actual-size to count
# (special cases: -1 to minimal size, 0 to maximal size)]
def _load_ext_histogram():
    return _load_from_w('ext_histogram')


# extension_names, dictionary of extension.lower() to array of orig_extension
def _load_ext_names():
    return _load_from_w('ext_vers')


# tuple of extension_histogram and extension_names
def load_ext():
    """
    Loads affect file-extensions histogram and names table
    :return: (histogram, names)
    """
    return _load_ext_histogram(), _load_ext_names()
