"""
Manage file access
"""

from .my_env import\
    rescue_folder, last_rescue_folder, rescued_file, data_file, data_backup, nas_to_pc,\
    archive_folder

__all__ = ['rescue_folder', 'last_rescue_folder', 'rescued_file', 'data_file', 'data_backup',
           'nas_to_pc', 'archive_folder']
