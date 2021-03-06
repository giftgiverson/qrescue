"""
Implement handling duplicate rescued files which
"""

from os.path import exists
from os import remove
from re import search as regex_match
from hashlib import md5
from my_env import rescued_file, data_file, data_backup
from matches import load_matches


def _get_md5(path):
    hash_md5 = md5()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _squash_duplicate(duplicates_file, matching, from_id):
    if len(matching.matches) == 1\
            or not any(match for match in matching.matches
                       if int(matching.matches[0].id) >= from_id):
        return matching
    unique = {}
    for match in matching.matches:
        checksum = _get_md5(match.path)
        if checksum in unique:
            print('SAME MD5: ' + match.path + ' ' + str(unique[checksum]))
            duplicates_file.write(match.path + ', ' + ', '.join(unique[checksum]) + '\n')
        else:
            unique[checksum] = match
    squashed = matching.clone()
    squashed.replace_matches(unique.values())
    return squashed


def _squash_duplicates(multi_matched, from_id):
    with data_file('squashed_multi_matched.csv', 'w') as squashed_file:
        with data_file('duplicates.csv', 'w') as duplicates_file:
            for matching in multi_matched:
                unique = _squash_duplicate(duplicates_file, matching, from_id)
                squashed_file.write(unique.serialize() + '\n')


# duplicates, array of tuple(duplicate's path, base dir, base name)
def _load_duplicates(d_type):
    dups = []
    with data_file('' + d_type + 'duplicates.csv') as file:
        for line in file:
            dups.append(tuple(v.strip() for v in line.split(',')))
    return dups


def _get_sub_groups(data, group):
    top_match = -1
    for i, datum in enumerate(data):
        for j in range(0, i):
            if data[j][0] <= top_match:
                continue
            if datum[1] == data[j][1]:
                datum[0] = data[j][0]
            else:
                datum[0] = j
    sub_groups = {}
    for datum in data:
        key = ','.join([group[0], str(datum[0])])
        if key not in sub_groups:
            sub_groups[key] = []
        sub_groups[key].append(datum[2])
    return sub_groups


def _validate_groups(groups):
    new_groups = {}
    for group in groups.items():
        if len(group[1]) == 1:
            new_groups[group[0]] = group[1]
            continue
        while True:
            data = [[0, control[0].read(4096), control] for control in group[1]]
            if not data[0][1]:
                ssub_groups = {group[0]: group[1]}
                break
            sub_groups = _get_sub_groups(data, group)
            if len(sub_groups) > 1:
                ssub_groups = _validate_groups(sub_groups)
                break
        new_groups.update(ssub_groups)
    return new_groups


def _validate_batch(base, batch, v_dups):
    print(base)
    targets = [(base, None)] + [(dup[0], dup) for dup in batch]
    # pylint: disable=consider-using-with
    target_controls = [(open(f, 'rb'), dup) for f, dup in targets]
    target_groups = {'0': target_controls}
    new_groups = _validate_groups(target_groups)
    for _, controls in new_groups.items():
        is_first = True
        base = None
        for control in controls:
            control[0].close()
            if is_first:
                is_first = False
                if control[1]:
                    base_name = control[1][0]
                    print('REINSTATING: ' + base_name)
                    base = ','.join(regex_match(r'\.(\d+)\\([^,]+)', base_name).groups())
                continue
            if base:
                v_dups.write(', '.join([control[1][0], base]))
            else:
                v_dups.write(', '.join(control[1]) + '\n')


def _validate_duplicates(raw_duplicates):
    cur_base = ''
    cur_batch = []
    with data_file('valid_duplicates.csv', 'w') as v_dups:
        for dup in raw_duplicates:
            base = rescued_file(dup[1], dup[2])
            if base != cur_base:
                if cur_batch:
                    _validate_batch(cur_base, cur_batch, v_dups)
                cur_base = base
                cur_batch = []
            cur_batch.append(dup)
        if cur_batch:
            _validate_batch(cur_base, cur_batch, v_dups)


def _remove_duplicates(valid_duplicates):
    cur_base = ''
    for dup in valid_duplicates:
        base = ', '.join(dup[1:])
        if cur_base != base:
            cur_base = base
            print(base)
        if exists(dup[0]):
            remove(dup[0])
            # print('REMOVING: ' + path)
        else:
            print('MISSING: ' + dup[0])


def _derefernce_duplicates(valid_duplicates, from_id):
    dups = {}
    for dup in valid_duplicates:
        folder, file = tuple(regex_match(r'(\d+)\\(.*)', dup[0]).groups())
        if folder not in dups:
            dups[folder] = []
        dups[folder].append(file)
    last_folder = '0'
    backup = data_backup('matched.csv')
    with data_file('matched.csv', 'w') as m_new:
        with data_file(backup) as m_old:
            for line in m_old:
                folder, file = tuple([v.strip() for v in line.split(',')][3:])
                if int(folder) < from_id or folder not in dups or file not in dups[folder]:
                    m_new.write(line)
                    continue
                if last_folder != folder:
                    last_folder = folder
                    print(folder)


def update_and_remove_duplicates(from_id):
    """
    Detect and remove binary-identical recovered files, leaving only one
    :param from_id: Start of recovery folder range not yet checked for duplicates
    """
    matches = load_matches('multi_')
    print('UPDATING DUPLICATES\n================')
    _squash_duplicates(matches, from_id)
    duplicates = _load_duplicates('')
    print('VALIDATING DUPLICATES\n================')
    _validate_duplicates(duplicates)
    print('REMOVING DUPLICATES\n================')
    duplicates = _load_duplicates('valid_')
    _remove_duplicates(duplicates)
    print('DE-REFERENCING DUPLICATES\n================')
    _derefernce_duplicates(duplicates, from_id)
