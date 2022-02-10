"""
Implement managing recovery operations
"""

from os import path, remove, utime
from shutil import copy
from matches import load_matches, get_match_key
from affected import load_affected, update_files
from my_env import affected_folder, rescued_file, archive_match, data_file


# pylint: disable=too-few-public-methods
class Recovery:
    """
    Perform file recovery
    """
    def __init__(self):
        folders, files = load_affected()
        self.folders = {folder[0]: folder for folder in folders}
        self.files = [list(file) for file in files]
        self.keyed_files = self._make_keyed_files()

    def _make_keyed_files(self):
        keyed_files = {}
        for file in self.files:
            key = file[2]+'.'+str(file[3])
            if key not in keyed_files:
                keyed_files[key] = []
            keyed_files[key].append(file)
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
        update_files(self.files)
        print(f'RECOVERED {len(matches)} Single Matched')

    @staticmethod
    def _get_single_un_recovered(affected):
        if len(affected) != 1:
            print(f'EXPECTED SINGLE MATCH, FOUND: {affected}')
            return None
        if affected[0][0] != "_":
            print(f'ALREADY RECOVERED: {affected}')
            return None
        return affected[0]

    def _get_affected(self, match):
        key = get_match_key(match)
        return self.keyed_files[key] if key in self.keyed_files else []

    def _recover(self, affected, match, submatch, recovered_file):
        affected_path, match_path = self._make_paths(affected, match, submatch)
        if affected_path:
            self._replace_7z(affected, affected_path, match_path)
        affected[0] = submatch
        recovered_file.write(', '.join([str(v) for v in affected]) + '\n')
        return affected_path

    def _make_paths(self, affected, match, submatch):
        affected_path = path.join(affected_folder(self.folders[affected[1]]), affected[5])
        match_path = rescued_file(match[3][submatch][0], match[3][submatch][1])
        if not path.exists(match_path):
            print(f'WARNING: MATCH FILE ALREADY ARCHIVED: {match_path},'
                  f' for {affected} at {affected_path}')
            return None, None
        return affected_path, match_path

    @staticmethod
    def _replace_7z(affected, affected_path, match_path):
        if path.exists(affected_path):
            print(f'WARNING: AFFECTED EXISTS: {affected_path}')
        copy(match_path, affected_path)
        utime(affected_path, (affected[4], affected[4]))
        z_path = affected_path + '.7z'
        if not path.exists(z_path):
            print(f'WARNING: 7z MISSING: {z_path}')
        else:
            remove(affected_path + '.7z')
