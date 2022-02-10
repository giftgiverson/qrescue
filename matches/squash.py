"""
Separate multi-matched and single-matched rescued files
"""

from matches import load_matches
from my_env import data_file


def _squash_matches(matches):
    squashed = {}
    for match in matches:
        key = match.key
        if key not in squashed:
            squashed[key] = match.clone()
        else:
            squashed[key].append(match)
    return [tuple(v) for v in squashed.values()]


def _sort_squashed(squashed):
    with data_file('single_matched.csv', 'w') as single_file:
        with data_file('multi_matched.csv', 'w') as multi_file:
            for match in squashed:
                line = match.serialize() + '\n'
                if match.is_single:
                    single_file.write(line)
                else:
                    multi_file.write(line)


def squash_matched():
    """
    Squashes matches by detecting single-matches, and grouping multi-matches by affected
    """
    matches = load_matches('', True)
    squashed = _squash_matches(matches)
    _sort_squashed(squashed)
