"""
Implement scanning for matches in rescued files
"""

from os import listdir
from os.path import join as pjoin, getsize
from re import search as regex_match

from affected import Index
import my_env


# pylint: disable=too-few-public-methods
class RecupScanner:
    """Recovered folder scanner"""
    def __init__(self):
        self._index = Index()

    def scan_recup(self, id_from, id_to):
        """
        Scan recovered folders for matches, reporting to matched and unmatched CSV files
        :param id_from: Start of range of folder IDs to scan (inclusive)
        :param id_to: End of range of folder IDs to scan (inclusive)
        """
        m_size = 0
        u_size = 0
        with my_env.data_file('matched.csv', 'a') as matched_file:
            with my_env.data_file('unmatched.csv', 'a') as unmatched_file:
                with my_env.data_file('scan_report.csv', 'a') as report_file:
                    for folder_id in range(id_from, id_to + 1):
                        m_s, u_s = self._scan_recup_dir(folder_id, matched_file, unmatched_file)
                        self._report_folder(folder_id, report_file, m_s, u_s)
                        m_size += m_s
                        u_size += u_s
        self._print_summary(m_size, u_size)

    def _scan_recup_dir(self, folder_id, matched_file, unmatched_file):
        id_path = my_env.rescue_folder(str(folder_id))
        m_size = 0
        u_size = 0
        for f_name in listdir(id_path):
            f_path = pjoin(id_path, f_name)
            f_ext: str = regex_match(r'\.([^.]+)$', f_path).group(1).lower()
            f_size = getsize(f_path)
            match_count, match_ext_names = self._index.get_matches(f_ext, f_size)
            report = \
                ', '.join(
                    [str(match_count), '|'.join(match_ext_names),
                     str(f_size), str(folder_id), f_name])\
                + '\n'
            if match_count:
                matched_file.write(report)
                m_size += f_size
            else:
                unmatched_file.write(report)
                u_size += f_size
        return m_size, u_size

    def _print_summary(self, m_size, u_size):
        print(f'== Matched {m_size / u_size * 100:.2f}%,'
              f' {"GB of ".join([f"{s / (1 << 30):.4f}" for s in [m_size, u_size]])}GB')
        a_size = self._index.total_size
        print(f'== Recovering up to {m_size / a_size * 100:.4f}%,'
              f' {"GB of ".join([f"{s / (1 << 30):.4f}" for s in [m_size, a_size]])}GB')

    @staticmethod
    def _report_folder(folder_id, report_file, m_s, u_s):
        report = ', '.join([my_env.rescue_folder(str(folder_id)), str(m_s), str(u_s)]) + '\n'
        print(report)
        report_file.write(report)
