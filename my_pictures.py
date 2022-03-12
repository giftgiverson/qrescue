import glob
import re
import os
import subprocess
import shutil

LOCAL_ROOM = 'f:\\4TBRed\\My Pictures\\Lightroom\\'
REAL_ROOM = 'z:\\My Pictures\\Lightroom\\'
NEGATIVES = 'z:\\Archive\\Negatives\\'
CONVERTER = 'C:\\Program Files\\Adobe\\Adobe DNG Converter\\Adobe DNG Converter.exe'


def collect():
    local_files = []
    for file_path in glob.glob(LOCAL_ROOM + '**/*.dng.7z', recursive=True):
        # date, file, real-directory
        local_files.append(list(re.search(r'(\d{4}-\d\d-\d\d)\\([^.]+)',
                                          file_path).groups())
                           + [os.path.dirname(file_path).replace(LOCAL_ROOM, REAL_ROOM)])
    local_files = sorted(local_files, key=lambda x: x[0])
    # print(local_files)
    negative_folders = []
    for dir_path in os.listdir(NEGATIVES):
        for subdir in os.listdir(os.path.join(NEGATIVES, dir_path)):
            if '_' in subdir:
                continue
            negative_folders.append(subdir)
    negative_folders = sorted(negative_folders)
    # print(negative_folders)
    cur_negative = -1
    cur_negative_files = {}
    with open(r'c:\\buff\\mypic.log', 'a') as log:
        for local_file in local_files:
            date, file, destination = local_file
            while True:
                if file in cur_negative_files:
                    source_file = cur_negative_files[file].replace('/', '\\')
                    message = f'Use {source_file} to recover into {destination}'
                    print(message)
                    if source_file.lower().endswith('cr2'):
                        try:
                            subprocess.check_call([CONVERTER, '-d', destination, source_file])
                            archive_trigger(date, file, destination)
                        except:
                            print(f'WARNING: Conversion failed to {local_file}')
                            log.write(f'Unable to {message}, failed to convert to {local_file}\n')
                        break
                    if source_file.lower().endswith('dng'):
                        shutil.copy(source_file,
                                    os.path.join(destination, os.path.basename(source_file)))
                        archive_trigger(date, file, destination)
                        break
                    print(f'WARNING: Can\'t hande: {local_file}')
                    log.write(f'Unable to {message}, cannot handle {local_file}\n')
                    break
                if cur_negative >= 0 and date <= negative_folders[cur_negative]:
                    print(f'WARNING: Can\'t recover: {local_file}')
                    log.write(f'Unable to recover: {local_file}\n')
                    break
                cur_negative += 1
                cur_negative_name = negative_folders[cur_negative]
                cur_negative_files = {os.path.basename(file_path).split('.')[0]: file_path
                                      for file_path in
                                      glob.glob(os.path.join(NEGATIVES,
                                                             cur_negative_name.split('-')[0],
                                                             cur_negative_name) + '/*')}
                # print(cur_negative_files)


def archive_trigger(date, file, target_dir):
    shutil.move(
        os.path.join(target_dir.replace(REAL_ROOM, LOCAL_ROOM), file + '.dng.7z'),
        os.path.join('C:/buff', f'{date}-{file}.dng.7z'))
