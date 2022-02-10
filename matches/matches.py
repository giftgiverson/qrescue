"""
Implement matching rescued files to affected files
"""

from os.path import join as pjoin, exists
from os import listdir, remove
from re import search as regex_match

from my_env import RESCUE_FOLDER, data_file, rescue_folder, RESCUE_FOLDER_PREFIX, data_backup

from .recup_scanner import _RecupScanner


def _parse_match(line):
    parts = line.split(',')
    return \
        int(parts[0]), parts[1].strip(), int(parts[2]), \
        [tuple(p.strip() for p in parts[n * 2 - 1:n * 2 + 1])
         for n in range(2, 1 + len(parts) >> 1)]


def load_matches(match_type):
    """
    Load match objects from file
    :param match_type: match file prefix
    :return: array of tuple(
        count, |-delimited extensions, size,
        array of tuple (recup_dir_id, file name))
    """
    matches = []
    with data_file(match_type + 'matched.csv') as file:
        for line in file:
            matches.append(_parse_match(line))
    return matches


def _remove_unmatched(unmatched):
    last_id = -1
    cur_dir = ''
    for non_matching in unmatched:
        cur_id, f_name = non_matching[3][0]
        if last_id != cur_id:
            last_id = cur_id
            cur_dir = rescue_folder(cur_id)
            print(cur_dir)
        f_path = pjoin(cur_dir, f_name)
        if exists(f_path):
            remove(f_path)
            # print('REMOVING: ' + path)
        else:
            print('MISSING: ' + f_path)


def _detect_next_range():
    to_id = max([int(m.group(1))
                 for m in [regex_match(RESCUE_FOLDER_PREFIX + r'\.(\d+)', f)
                           for f in listdir(RESCUE_FOLDER)] if m]
                ) - 1
    from_id = max([int(m[3][0][0]) for m in load_matches('')]) + 1
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
    _remove_unmatched(load_matches('un'))
    data_backup('unmatched.csv', '_removed')
    return from_id


def _squash_matches(matches):
    squashed = {}
    for match in matches:
        key = get_match_key(match)
        if key not in squashed:
            squashed[key] = list(match)
        else:
            existing = squashed[key]
            existing[0] += match[0]
            existing[3] += match[3]
    return [tuple(v) for v in squashed.values()]


def get_match_key(match):
    """
    Calculates the key of a match
    :param match: match
    :return: match key "extension.size"
    """
    return match[1] + '.' + str(match[2])


def encode_match(match):
    """
    Encodes a match object to string
    :param match: match
    :return: string encoding match
    """
    return ', '.join([str(v) for v in match[:3]] + [a for b in match[3] for a in b]) + '\n'


def _sort_squashed(squashed):
    with data_file('single_matched.csv', 'w') as single_file:
        with data_file('multi_matched.csv', 'w') as multi_file:
            for match in squashed:
                line = encode_match(match)
                if match[0] == 1:
                    single_file.write(line)
                else:
                    multi_file.write(line)


def squash_matched():
    """
    Squashes matches by detecting single-matches, and grouping multi-matches by affected
    """
    matches = load_matches('')
    squashed = _squash_matches(matches)
    _sort_squashed(squashed)
