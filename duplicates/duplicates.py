import os
import re
import hashlib
import datetime
from matches import encode_match, load_matches


def _get_md5(path):
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _squash_duplicates_line(duplicates_file, mm_line, from_id):
    if len(mm_line[3]) == 1 or not any([match for match in mm_line[3] if int(mm_line[3][0][0]) >= from_id]):
        return mm_line[3]
    unique = {}
    for match in mm_line[3]:
        path = os.path.join('f:/share/recup_dir.' + match[0], match[1])
        md5 = _get_md5(path)
        if md5 in unique:
            print('SAME MD5: ' + path + ' ' + str(unique[md5]))
            duplicates_file.write(path + ', ' + ', '.join(unique[md5]) + '\n')
        else:
            unique[md5] = match
    return unique.values()


def _squash_duplicates(multi_matched, from_id):
    with open('w:/squashed_multi_matched.csv', 'w', encoding='utf8') as squashed_file:
        with open('w:/duplicates.csv', 'w', encoding='utf8') as duplicates_file:
            for mm_line in multi_matched:
                unique = _squash_duplicates_line(duplicates_file, mm_line, from_id)
                sq_line = list(mm_line)
                sq_line[0] = int(mm_line[0] / len(mm_line[3])) * len(unique)
                sq_line[3] = unique
                squashed_file.write(encode_match(sq_line))


# duplicates, array of tuple(duplicate's path, base dir, base name)
def _load_duplicates(d_type):
    dups = []
    with open('w:/' + d_type + 'duplicates.csv', encoding='utf8') as f:
        for line in f:
            dups.append(tuple([v.strip() for v in line.split(',')]))
    return dups


def _get_sub_groups(data, group):
    top_match = -1
    for i in range(0, len(data)):
        for j in range(0, i):
            if data[j][0] <= top_match:
                continue
            if data[i][1] == data[j][1]:
                data[i][0] = data[j][0]
            else:
                data[i][0] = j
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
                    base = ','.join(re.search(r'\.(\d+)\\([^,]+)', base_name).groups())
                continue
            if base:
                v_dups.write(', '.join([control[1][0], base]))
            else:
                v_dups.write(', '.join(control[1]) + '\n')


def _validate_duplicates(raw_duplicates):
    cur_base = ''
    cur_batch = []
    with open('w:/valid_duplicates.csv', 'w', encoding='utf8') as v_dups:
        for dup in raw_duplicates:
            base = os.path.join('f:/share/recup_dir.' + dup[1], dup[2])
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
        if os.path.exists(dup[0]):
            os.remove(dup[0])
            # print('REMOVING: ' + path)
        else:
            print('MISSING: ' + dup[0])


def _derefernce_duplicates(valid_duplicates, from_id):
    dups = {}
    for dup in valid_duplicates:
        folder, file = tuple(re.search(r'(\d+)\\(.*)', dup[0]).groups())
        if folder not in dups:
            dups[folder] = []
        dups[folder].append(file)
    last_folder = '0'
    old_matched_name = 'w:/matched' + datetime.datetime.utcnow().strftime('%y-%m-%d_%H_%M_%S') + '.csv'
    os.rename('w:/matched.csv', old_matched_name)
    with open('w:/matched.csv', 'w', encoding='utf8') as m_new:
        with open(old_matched_name, encoding='utf8') as m_old:
            for line in m_old:
                folder, file = tuple([v.strip() for v in line.split(',')][3:])
                if int(folder) < from_id or folder not in dups or file not in dups[folder]:
                    m_new.write(line)
                    continue
                if last_folder != folder:
                    last_folder = folder
                    print(folder)


def update_and_remove_duplicates(from_id):
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
