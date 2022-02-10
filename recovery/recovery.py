"""
Implement managing recovery operations
"""

from os import path
from matches import load_matches, get_match_key
from affected import load_files, update_files
from my_env import rescued_file, archive_match, data_file


# pylint: disable=too-few-public-methods
class Recovery:
    """
    Perform file recovery
    """
    def __init__(self):
        self._files = load_files()
        self._keyed_files = self._make_keyed_files()

    def _make_keyed_files(self):
        keyed_files = {}
        for file in self._files:
            if file.key not in keyed_files:
                keyed_files[file.key] = []
            keyed_files[file.key].append(file)
        return keyed_files

    def recover_single_matched(self):
        """
        Recover single-matched files
        """
        matches = load_matches('single_')
        last_folder = 0
        with data_file('recovered.csv', 'a') as recovered_file:
            for match in matches:
                if last_folder != match[3][0][0]:
                    last_folder = match[3][0][0]
                    print(last_folder)
                affected = self._get_single_un_recovered(self._get_affected(match))
                if affected and self._recover(affected, match, 0, recovered_file):
                    archive_match(match)
        update_files(self._files)
        print(f'RECOVERED {len(matches)} Single Matched')

    @staticmethod
    def _get_single_un_recovered(affected_list):
        if len(affected_list) != 1:
            print(f'EXPECTED SINGLE MATCH, FOUND: {affected_list}')
            return None
        if affected_list[0].is_matched:
            print(f'ALREADY RECOVERED: {affected_list[0]}')
            return None
        return affected_list[0]

    def _get_affected(self, match):
        key = get_match_key(match)
        return self._keyed_files[key] if key in self._keyed_files else []

    def _recover(self, affected, match, submatch, recovered_file):
        match_path = self._make_path(affected, match, submatch)
        if match_path:
            affected.apply_match(match_path, submatch)
        recovered_file.write(affected.serialize() + '\n')
        return match_path

    @staticmethod
    def _make_path(affected, match, submatch):
        match_path = rescued_file(match[3][submatch][0], match[3][submatch][1])
        if not path.exists(match_path):
            print(f'WARNING: MATCH FILE ALREADY ARCHIVED: {match_path}, for {affected}')
            return None
        return match_path
