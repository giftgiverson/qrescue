from os.path import join as pjoin
from os import rename
from datetime import datetime

data_folder = 'w:/'
rescue_share = 'f:/share'
rescue_folder_prefix = 'recup_dir'


def rescue_folder(f_id):
    return pjoin(rescue_share, rescue_folder_prefix + '.' + f_id)


def rescued_file(f_id, f_name):
    return pjoin(rescue_folder(f_id), f_name)


def data_file(f_name, mode='r'):
    return open(pjoin(data_folder, f_name), mode, encoding='utf8')


def data_backup(f_name, label=''):
    backup_name = (label + datetime.utcnow().strftime('%y-%m-%d_%H_%M_%S') + '.').join(f_name.split('.'))
    rename(pjoin(data_folder, f_name), pjoin(data_folder, backup_name))
    return backup_name
