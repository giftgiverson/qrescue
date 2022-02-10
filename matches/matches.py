"""
Handle rescued files
"""

from os.path import join as pjoin, exists
from os import remove, mkdir
from shutil import move

from my_env import data_file, rescue_folder, archive_folder
from my_misc import static_vars


class Recuperated:
    """
    Recuperated file
    """
    # pylint: disable=invalid-name
    @property
    def id(self):
        """
        :return: (string) id of recuperated folder
        """
        return self._id

    @property
    def path(self):
        """
        :return: (string) path to recuperated file
        """
        return self._path

    def __init__(self, detail):
        self._id, self._name = detail
        self._path = pjoin(rescue_folder(self._id), self._name)

    def archive(self):
        """
        Moves match file to archive folder
        """
        folder = archive_folder(self._id)
        if not exists(folder):
            mkdir(folder)
        move(self.path, folder)

    def remove(self):
        """
        Removes match file
        """
        if exists(self._path):
            remove(self._path)
            # print('REMOVING: ' + path)
        else:
            print('MISSING: ' + self._path)

    def serialize(self):
        """
        :return: (string) serialization
        """
        return ','.join([self._id, self._name])


class Matching:
    """
    Matching recuperated files
    """
    @property
    def key(self):
        """
        :return: match key
        """
        return self._key

    @property
    def affected_count(self):
        """
        :return: number of affected files matched
        """
        return self._affected_count

    @property
    def is_single(self):
        """
        :return: (bool) is this a single-match
        """
        return self._affected_count == 1 and len(self._matches) == 1

    @property
    def is_paired(self):
        """
        :return: (bool) is there a match for every affected file with this key
        """
        return self._affected_count == len(self._matches)

    @property
    def matches(self):
        """
        :return: matching recuperated files
        """
        return self._matches

    def __init__(self, line):
        parts = line.split(',')
        self._head = ','.join(parts[1:3])
        ext = [e.lower() for e in parts[1].split('|')][0]
        self._key = '.'.join([ext, parts[2]])
        self._matches = \
            [Recuperated(p.strip() for p in parts[n * 2 - 1:n * 2 + 1])
             for n in range(2, 1 + len(parts) >> 1)]
        self._affected_count = int(int(parts[0] / len(self._matches)))

    def append(self, matched):
        """
        Append matches of the same key
        :param matched: matches of the same key
        """
        if matched.key == self._key:
            self._matches.append(matched.matches)

    def serialize(self):
        """
        Serializes this object to a string line
        :return: (string) serialization (without newline)
        """
        return ', '.join(
            [str(self._affected_count * len(self._matches)), self._head]
            + [match.serialize() for match in self._matches])

    def clone(self):
        """
        Create a clone with no reference to this original
        :return: Matching clone
        """
        return Matching(self.serialize())


@static_vars(matches_by_type={})
def load_matches(match_type, refresh=False):
    """
    Load match objects from file
    :param match_type: match file prefix
    :param refresh: should the matches be re-read from file
    :return: array of Matching
    """
    if refresh or match_type not in load_matches.matches_by_type:
        matches = []
        with data_file(match_type + 'matched.csv') as file:
            for line in file:
                matches.append(Matching(line))
        load_matches.matches_by_type[match_type] = matches
    return load_matches.matches_by_type[match_type]
