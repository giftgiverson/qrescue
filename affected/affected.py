"""
Implements handling of affected files
"""

from my_env import data_file, data_backup

AFFECTED_FILES_CSV = 'affected_files.csv'


def _parse_folder(line):
    parts = line.split(',')
    return parts[0], ','.join(parts[1:]).strip()


# folders, array or tuple(ID, path)
def _load_folders():
    read_folders = []
    with data_file('affected_folders.csv') as file:
        for line in file:
            read_folders.append(_parse_folder(line))
    return read_folders


# files, array of tuple(state, folder_id, orig_extension, size, ctime, name without .7z at the end)
def _parse_file(line):
    parts = line.split(',')
    return tuple([part.strip() for part in
                  parts[:3]] + [int(parts[3]), float(parts[4]), ','.join(parts[5:]).strip()])


def _load_files():
    read_files = []
    with data_file(AFFECTED_FILES_CSV) as file:
        for line in file:
            read_files.append(_parse_file(line))
    return read_files


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


# tuple of folder, files
def load_affected():
    """
    Loads affected folders and files
    :return: (folders, files)
    """
    return _load_folders(), _load_files()


# tuple of extension_histogram and extension_names
def load_ext():
    """
    Loads affect file-extensions histogram and names table
    :return: (histogram, names)
    """
    return _load_ext_histogram(), _load_ext_names()


def update_files(affected_files):
    """
    Update affected files (backing up previous version)
    :param affected_files: updated affected files
    """
    data_backup(AFFECTED_FILES_CSV)
    with data_file(AFFECTED_FILES_CSV, 'w') as file:
        for affected in affected_files:
            file.write(', '.join(str(v) for v in affected) + '\n')
