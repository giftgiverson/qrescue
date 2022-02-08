"""
Manage file access
"""

from .my_env import\
    RESCUE_FOLDER, rescue_folder, rescued_file, RESCUE_FOLDER_PREFIX,\
    DATA_FOLDER, data_file, data_backup

__all__ = ['RESCUE_FOLDER', 'rescue_folder', 'rescued_file', 'RESCUE_FOLDER_PREFIX',
           'DATA_FOLDER', 'data_file', 'data_backup']
