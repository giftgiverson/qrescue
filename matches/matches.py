"""
Handle rescued files
"""

import os
import shutil
import my_env
from affected import FileBase
from my_misc import static_vars


class Recuperated(FileBase):
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

    def __init__(self, detail):
        self._id, name = detail
        path = os.path.join(my_env.rescue_folder(self._id), name)
        super().__init__(name, path)

    def archive(self):
        """
        Moves match file to archive folder
        """
        folder = my_env.archive_folder(self._id)
        if not os.path.exists(folder):
            os.mkdir(folder)
        shutil.move(self.path, folder)

    def remove(self):
        """
        Removes match file
        """
        if os.path.exists(self._path):
            os.remove(self._path)
            # print('REMOVING: ' + path)
        else:
            print('MISSING: ' + self._path)

    def serialize(self):
        """
        :return: (string) serialization
        """
        return ', '.join([self._id, self._name])

    def __repr__(self):
        """returns a string representation of this object"""
        return self.serialize()


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
        self._head = ','.join(parts[1:3]).strip()
        ext = [e.lower() for e in parts[1].split('|')][0].strip()
        self._key = '.'.join([ext, parts[2].strip()])
        self._matches = \
            [Recuperated(p.strip() for p in parts[n * 2 - 1:n * 2 + 1])
             for n in range(2, 1 + len(parts) >> 1)]
        self._affected_count = int(int(parts[0]) / len(self._matches))

    def replace_matches(self, new_matches):
        """
        Clear all recuperated from the matches list
        """
        self._matches = new_matches

    def append(self, matched):
        """
        Append matches of the same key
        :param matched: matches of the same key
        """
        if matched.key == self._key:
            total_affected = self._affected_count * len(self._matches)
            self._matches += matched.matches
            self._affected_count = int(total_affected / len(self._matches))

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

    def __repr__(self):
        """returns a string representation of this object"""
        return self.serialize()


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
        with my_env.data_file(match_type + 'matched.csv') as file:
            for line in file:
                matches.append(Matching(line))
        load_matches.matches_by_type[match_type] = matches
    return load_matches.matches_by_type[match_type]
