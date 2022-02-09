"""
Implement managing recovery operations
"""

from os import path
from shutil import copy
from matches import load_matches, get_match_key
from affected import load_affected
from my_env import affected_folder, rescued_file, archive_match


# pylint: disable=too-few-public-methods
class Recovery:
    """
    Perform file recovery
    """
    def __init__(self):
        folders, self.files = load_affected()
        self.folders = {folder[0]: folder for folder in folders}

    def recover_single_matched(self):
        """
        Recover single-matched files
        """
        matches = load_matches('single_')
        recovered = 0
        last_folder = 0
        for match in matches:
            if last_folder != match[3]:
                last_folder = match[3]
                print(last_folder)
            affected = self._get_affected_paths(match)
            if len(affected) != 1:
                print(f"EXPECTED SINGLE MATCH, FOUND: {affected}")
                continue
            if self._recover(affected[0], match):
                recovered += 1
                archive_match(match)
        print(f"RECOVERED {recovered / len(matches):.2f}% of Single Matched:"
              f" {recovered} out of {len(matches)}")

    def _get_affected_paths(self, match):
        key = get_match_key(match)
        return [file for file in self.files if key == file[2]+'.'+file[3]]

    def _recover(self, affected, match):
        affected_path = path.join(affected_folder(self.folders[affected[1]]), affected[5])
        match_path = rescued_file(match[3], match[4])
        if not path.exists(match_path):
            print(f"MISSING MATCH FILE: {match_path}, for {affected} at {affected_path}")
            return False
        copy(match_path, affected_path)
        return True
