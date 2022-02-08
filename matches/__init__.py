"""
Match rescued files to affected files
"""

from .matches import update_matched_remove_unmatched, load_matches, squash_matched, encode_match

__all__ = ['update_matched_remove_unmatched', 'load_matches', 'squash_matched', 'encode_match']
