from my_env import rescue_share, data_file, rescue_folder, rescue_folder_prefix, data_backup
from os.path import join as pjoin, exists, getsize
from os import listdir, remove
from re import search as regex_match
from affected import load_ext


class _RecupScanner:
    def __init__(self):
        self.ext_histogram, self.ext_names = load_ext()

    def scan_recup(self, id_from, id_to):
        m_size = 0
        u_size = 0
        with data_file('matched.csv', 'a') as matched_file:
            with data_file('unmatched.csv', 'a') as unmatched_file:
                with data_file('scan_report.csv', 'a') as report_file:
                    for folder_id in range(id_from, id_to + 1):
                        m_s, u_s = self._scan_recup_dir(folder_id, matched_file, unmatched_file)
                        m_size += m_s
                        u_size += u_s
                        report = ', '.join(['recup_dir.' + str(folder_id), str(m_s), str(u_s)]) + '\n'
                        print(report)
                        report_file.write(report)
        print(f'== Matched {m_size / u_size * 100:.2f}%,'
              f' {"GB of ".join([f"{s / (1 << 30):.4f}" for s in [m_size, u_size]])}GB')
        a_size = sum(v[0]*v[1] for e in self.ext_histogram.values() for v in e.items() if v[0] > 0)
        print(f'== Recovering up to {m_size / a_size * 100:.4f}%,'
              f' {"GB of ".join([f"{s / (1 << 30):.4f}" for s in [m_size, a_size]])}GB')

    def _scan_recup_dir(self, folder_id, matched_file, unmatched_file):
        id_path = rescue_folder(str(folder_id))
        m_size = 0
        u_size = 0
        for f_name in listdir(id_path):
            f_path = pjoin(id_path, f_name)
            f_ext: str = regex_match('\\.([^.]+)$', f_path).group(1).lower()
            f_size = getsize(f_path)
            match_ext_names = []
            match_count = 0
            if f_ext in self.ext_names:
                for ext in self.ext_names[f_ext]:
                    if f_size in self.ext_histogram[ext]:
                        match_ext_names.append(ext)
                        match_count += self.ext_histogram[ext][f_size]
            report = \
                ', '.join([str(match_count), '|'.join(match_ext_names), str(f_size), str(folder_id), f_name]) + '\n'
            if match_count:
                matched_file.write(report)
                m_size += f_size
            else:
                unmatched_file.write(report)
                u_size += f_size
        return m_size, u_size


def _parse_match(line):
    parts = line.split(',')
    return \
        int(parts[0]), parts[1].strip(), int(parts[2]), \
        [tuple([p.strip() for p in parts[n * 2 - 1:n * 2 + 1]]) for n in range(2, 1 + len(parts) >> 1)]


# matches, array of tuple(count, |-delimited extensions, size, array of tuple (recup_dir_id, file name))
def load_matches(match_type):
    matches = []
    with data_file(match_type + 'matched.csv') as f:
        for line in f:
            matches.append(_parse_match(line))
    return matches


def _remove_unmatched(unmatched):
    last_id = -1
    cur_dir = ''
    for um in unmatched:
        cur_id, f_name = um[3][0]
        if last_id != cur_id:
            last_id = cur_id
            cur_dir = rescue_folder(cur_id)
            print(cur_dir)
        f_path = pjoin(cur_dir, f_name)
        if exists(f_path):
            remove(f_path)
            # print('REMOVING: ' + path)
        else:
            print('MISSING: ' + f_path)


def _detect_next_range():
    to_id = max([int(m.group(1))
                 for m in [regex_match(rescue_folder_prefix + r'\.(\d+)', f)
                           for f in listdir(rescue_share)] if m]
                ) - 1
    from_id = max([int(m[3][0][0]) for m in load_matches('')]) + 1
    return from_id, to_id


def update_matched_remove_unmatched(is_last=False):
    from_id, to_id = _detect_next_range()
    if is_last:
        to_id += 1
    print(f'UPDATING MATCHED: from {from_id} to {to_id}\n====================')
    _RecupScanner().scan_recup(from_id, to_id)
    print('REMOVING UNMATCHED\n================')
    _remove_unmatched(load_matches('un'))
    data_backup('unmatched.csv', '_removed')
    return from_id


def _squash_matches(matches):
    squashed = {}
    for match in matches:
        key = match[1] + '.' + str(match[2])
        if key not in squashed:
            squashed[key] = list(match)
        else:
            existing = squashed[key]
            existing[0] += match[0]
            existing[3] += match[3]
    return [tuple(v) for v in squashed.values()]


def encode_match(match):
    return ', '.join([str(v) for v in match[:3]] + [a for b in match[3] for a in b]) + '\n'


def _sort_squashed(squashed):
    with data_file('single_matched.csv', 'w') as single_file:
        with data_file('multi_matched.csv', 'w') as multi_file:
            for match in squashed:
                line = encode_match(match)
                if match[0] == 1:
                    single_file.write(line)
                else:
                    multi_file.write(line)


def squash_matched():
    matches = load_matches('')
    squashed = _squash_matches(matches)
    _sort_squashed(squashed)
