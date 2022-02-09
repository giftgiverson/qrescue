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
                affected = self._get_affected(match)
                if len(affected) != 1:
                    print(f'EXPECTED SINGLE MATCH, FOUND: {affected}')
                    continue
                if self._recover(affected[0], match, 0, recovered_file):
                    archive_match(match)
        update_files(self.files)
        print(f'RECOVERED {len(matches)} Single Matched')

    def _get_affected(self, match):
        key = get_match_key(match)
        return [file for file in self.files if key == file[2]+'.'+str(file[3])]

    def _recover(self, affected, match, submatch, recovered_file):
        affected_path = path.join(affected_folder(self.folders[affected[1]]), affected[5])
        match_path = rescued_file(match[3][submatch][0], match[3][submatch][1])
        if not path.exists(match_path):
            print(f'WARNING MATCH FILE ALREADY ARCHIVED: {match_path},'
                  f' for {affected} at {affected_path}')
            return False
        if path.exists(affected_path):
            print(f'WARNING AFFECTED EXISTS: {affected_path}')
        copy(match_path, affected_path)
        utime(affected_path, (affected[4], affected[4]))
        z_path = affected_path + '.7z'
        if not path.exists(z_path):
            print(f'WARNING 7z MISSING: {z_path}')
        else:
            remove(affected_path + '.7z')
        affected[0] = submatch
        recovered_file.write(', '.join([str(v) for v in affected]))
        return True
