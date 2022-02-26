"""
Match rescued files to affected files
"""

from .matches import load_matches, Matching, Recuperated
from .squash import squash_matched
from .update import update_matched_remove_unmatched

__all__ = ['load_matches', 'squash_matched', 'update_matched_remove_unmatched', 'Matching',
           'Recuperated']
