"""
Implement managing recovery operations
"""

import os
import matches
import affected
import my_env


# pylint: disable=too-few-public-methods
class Recovery:
    """
    Perform file recovery
    """
    def __init__(self):
        self._files = affected.load_files()
        self._keyed_files = self._make_keyed_files()

    def _make_keyed_files(self):
        keyed_files = {}
        for file in self._files:
            if not file.needs_match:
                continue
            if file.key not in keyed_files:
                keyed_files[file.key] = []
            keyed_files[file.key].append(file)
        return keyed_files

    def mark_unrecoverable(self):
        """
        Locate and mark affected files which cannot be recovered
        """
        matched = matches.load_matches('', True)
        matchable_keys = {key: False for key, _ in self._keyed_files.items()}
        for match in matched:
            if match.key in matchable_keys:
                matchable_keys[match.key] = True
        new_keyed = {}
        count = 0
        for key, matchable in matchable_keys.items():
            if matchable:
                new_keyed[key] = self._keyed_files[key]
                continue
            for file in self._keyed_files[key]:
                count += 1
                file.mark_unmatchable()
        print(f'DETECTED {count} UNMATCHABLE AFFECTED FILES (out of {len(self._files)})')
        affected.update_files(self._files)
        self._keyed_files = new_keyed

    def recover_single_matched(self, handler):
        """
        Recover single-matched files
        """
        matched = matches.load_matches('single_', True)
        self._recover_matched(handler, matched)

    def recover_multi_matched(self, handler):
        """
        Recover multi-matched files
        """
        matched = matches.load_matches('squashed_multi_', True)
        self._recover_matched(handler, matched)

    def _recover_matched(self, handler, matched):
        last_folder = 0
        recovered = 0
        try:
            with my_env.data_file('recovered.csv', 'a') as recovered_log:
                for match in matched:
                    cur_folder = match.matches[0].id
                    if last_folder != cur_folder:
                        last_folder = cur_folder
                        print(last_folder)
                    if handler.can_handle(match):
                        for affected_file, submatch, archivable\
                                in handler.handle(match, self._get_affected(match)):
                            if self._recover(affected_file, match, submatch, recovered_log):
                                recovered += 1
                                if archivable:
                                    match.matches[submatch].archive()
        finally:
            affected.update_files(self._files)
            print(f'RECOVERED {recovered} Matched {handler.get_type()}')

    def _get_affected(self, match):
        key = match.key
        return self._keyed_files[key] if key in self._keyed_files else []

    def _recover(self, affected_file, match, submatch, recovered_log):
        match_path = self._make_path(affected_file, match, submatch)
        if match_path:
            affected_file.apply_match(match_path, submatch)
        recovered_log.write(affected_file.serialize() + '\n')
        return match_path

    @staticmethod
    def _make_path(affected_file, match, submatch):
        match_path = match.matches[submatch].path
        if not os.path.exists(match_path):
            print(f'WARNING: MATCH FILE ALREADY ARCHIVED: {match_path}, for {affected_file}')
            return None
        return match_path
