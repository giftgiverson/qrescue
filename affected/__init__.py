"""
Handles affected files
"""

from .index import Index
from .files import load_files, update_files, AffectedFile, FileBase
from .folders import load_folders

__all__ = ['Index', 'load_files', 'load_folders', 'update_files', 'AffectedFile', 'FileBase']
