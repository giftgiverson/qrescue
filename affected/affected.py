from my_env import data_file


def _parse_folder(line):
    parts = line.split(',')
    return parts[0], ','.join(parts[1:]).strip()


# folders, array or tuple(ID, path)
def _load_folders():
    read_folders = []
    with data_file('affected_folders.csv') as f:
        for line in f:
            read_folders.append(_parse_folder(line))
    return read_folders


# files, array of tuple(state, folder_id, orig_extension, size, ctime, name without .7z at the end)
def _parse_file(line):
    parts = line.split(',')
    return tuple([part.strip() for part in parts[:3]] + [int(parts[3]), float(parts[4]), ','.join(parts[5:]).strip()])


def _load_files():
    read_files = []
    with data_file('affected_files.csv') as f:
        for line in f:
            read_files.append(_parse_file(line))
    return read_files


def _load_from_w(file_name):
    with data_file(file_name + '.pyon') as file:
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
    return _load_folders(), _load_files()


# tuple of extension_histogram and extension_names
def load_ext():
    return _load_ext_histogram(), _load_ext_names()
