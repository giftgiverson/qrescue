"""
Implement matching rescued files to affected files
"""

from matches import load_matches
from my_env import last_rescue_folder, data_backup

from .recup_scanner import _RecupScanner


def _remove_unmatched(unmatched):
    last_id = -1
    for non_matching in unmatched:
        recup = non_matching.matches[0]
        if last_id != recup.id:
            last_id = recup.id
            print(last_id)
        recup.remove()


def _detect_next_range():
    to_id = last_rescue_folder() - 1
    from_id = max([int(m.matches[0].id) for m in load_matches('')]) + 1
    return from_id, to_id


def update_matched_remove_unmatched(is_last=False):
    """
    Scan new rescued files, match to affected files by extension and size, and delete rescued
     files which don't match any affected file
    :param is_last: (optional, default=False) Did PhotoRec finish running, so we can safely
     include the last recovery folder?
    :return: ID of first folder with new files
    """
    from_id, to_id = _detect_next_range()
    if is_last:
        to_id += 1
    print(f'UPDATING MATCHED: from {from_id} to {to_id}\n====================')
    _RecupScanner().scan_recup(from_id, to_id)
    print('REMOVING UNMATCHED\n================')
    _remove_unmatched(load_matches('un', True))
    data_backup('unmatched.csv', '_removed')
    return from_id
