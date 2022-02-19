"""
Getting picture-taken date from CR2
Based on:
 https://stackoverflow.com/questions/3696642/reading-a-cr2-raw-canon-image-header-using-python
"""
import struct
import datetime
import time
import re
import my_env

recognised_tags = {
    0x0132: 'dateTime'
}


def _get_header_from_cr2(buffer):
    return struct.unpack_from('HHLHBBL', buffer)


def _find_date_time_offset_from_cr2(buffer, ifd_offset, endian_flag):
    (num_of_entries,) = struct.unpack_from(endian_flag + 'H', buffer, ifd_offset)
    datetime_offset = -1
    for entry_num in range(0, num_of_entries):
        (tag_id, tag_type, num_of_value, value) = \
            struct.unpack_from(endian_flag + 'HHLL', buffer, ifd_offset + 2 + entry_num * 12)
        if tag_id == 0x0132:
            assert tag_type == 2
            assert num_of_value == 20
            datetime_offset = value
    return datetime_offset


def get_cr2_datetime_offset(path):
    """returns 'picture taken' timestamp read from CR2 header"""
    with open(path, 'rb') as cr2_file:
        buffer = cr2_file.read(1024)
        (byte_order, _, _, _, _, _, _) = _get_header_from_cr2(buffer)
        endian_flag = '>' if byte_order == 0x4D4D else ('<' if byte_order == 0x4949 else '@')
        datetime_offset = _find_date_time_offset_from_cr2(buffer, 0x10, endian_flag)
        datetime_b_string = struct.unpack_from(20 * 's', buffer, datetime_offset)
        datetime_string = ''.join([b.decode('utf-8') for b in datetime_b_string][:-1])
        f_date_time_dt = datetime.datetime.strptime(datetime_string, '%Y:%m:%d %H:%M:%S')
        return time.mktime(f_date_time_dt.timetuple())


def match_index_and_cr2_timestamp(matching):
    """return tuples of (match-index, CR2 timestamp)"""
    return [(i, get_cr2_datetime_offset(match.path))
            for i, match in enumerate(matching.matches)]


def affected_index_and_cr2_limits(affected_list):
    """return tuples of (affected-index, limits) where 'limits' is a list of 0-2 CR2 timestamps
     read from the same folder, for all items in affected_list:
    0 limits: no other CR2 found
    1 limit: one other CR2 found
    2 limits: these are the CR2 timestamps of the first and last CR2 file in the folder
     (by modified time)
    """
    return [(i, [get_cr2_datetime_offset(path)
                 for path in my_env.neighbor_modified_limits(affected.path)])
            for i, affected in enumerate(affected_list)]


def affected_index_and_folder_limits(affected_list, neighborhood):
    """return tuples of (affected-index, limits) where 'limits' is a list of 0-2 folder timestamps
     read from the names of the parent folder and its neighbors, for items in affected_list which
     don't have two edges in 'neighborhood':
    0 limits: parent's folder name isn't of the format YYYY-MM-DD
    2 limits: limits read from parent name, and its immediate predecessor (or start-of year if it
     is the first folder in its year)
    """
    return [(i, timestamps_from_names(my_env.parent_and_previous_folder(affected_list[i])))
            for i, edges in neighborhood if len(edges) != 2]


def handle_couples(matched, neighborhood, affected_match, match_affected):
    """tries to match affected by picture-time-taken range read from its neighbors"""
    for affected_index, edges in neighborhood:
        if len(edges) != 2:
            continue
        for match_index, match_cr2_timestamp in matched:
            if edges[0] <= match_cr2_timestamp <= edges[1]:
                affected_match[affected_index].append(match_index)
                match_affected[match_index] += 1


def _serialize_affected(affected):
    return [affected.folder_key, affected.name]


def _serialize_match(matched):
    match, index, matches = matched
    return [match.id, match.name, str(index), str(matches)]


def serialize_unhandled(match_key, unmatched, matchings):
    """returns CSV lines describing items in affected_match which can't be handled automatically:
    [match_key,
     num_of_unmatched_affected, unmatched_affected1, ..., unmatched_affectedN,
     num_of_matched, matched1, ..., matchedN]
    Where:
     unmatched_affected* = folder_key, name
     matched* = folder_id, name, submatch, unmatched_count
    matched list is sorted by descending unmatched_count (where -1 means archived match)
    """
    return ', '.join(
        [match_key, str(len(unmatched))] +
        [part for item in unmatched for part in _serialize_affected(item)] +
        [match_key, str(len(matchings))] +
        [part for item in matchings for part in _serialize_match(item)]
    ) + '\n'


def timestamps_from_names(names):
    """get timestamp from folders named YYYY_MM_DD,
     or from start of YYYY to one folder if only one name is given"""
    to_date = timestamp_from_name(names[0])
    if to_date < 0:
        return []
    if names[1]:
        from_date = timestamp_from_name(names[0])
    else:
        last_year = str(int(names[0].split('_')[0])-1)
        prev_year_end = '_'.join([last_year, '12', '31'])
        from_date = timestamp_from_name(prev_year_end)
    return [from_date, to_date]


def timestamp_from_name(name):
    """get timestamp from folder named YYYY_MM_DD"""
    if not re.search(r'\d{4}_\d{2}_\d{2}', name):
        return -1.0
    f_date_time_dt = datetime.datetime.strptime(name, '%Y_%m_%d')
    return time.mktime(f_date_time_dt.timetuple()) + 86400.0


class Cr2AutoHandler:
    """handle CR2 matches scanning"""
    def __init__(self):
        self._manual_file = None

    def __enter__(self):
        self._manual_file = my_env.data_file('manual_match', 'a')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._manual_file.close()

    @staticmethod
    def can_handle(match):
        """can handle CR2 matches"""
        return match.key.startswith('cr2')

    def handle(self, matching, affected_list):
        """handle CR2 match scanning"""
        if len(affected_list) == 0:
            return []
        matched = match_index_and_cr2_timestamp(matching)
        neighborhood = affected_index_and_cr2_limits(affected_list)
        neighborhood += affected_index_and_folder_limits(affected_list, neighborhood)
        affected_match = {i: [] for i in range(0, len(affected_list))}
        match_affected = {i: 0 for i in range(0, len(matching.matches))}
        handle_couples(matched, neighborhood, affected_match, match_affected)
        return list(self._process_matching(matching, affected_list, affected_match, match_affected))

    @staticmethod
    def get_type():
        """handler type"""
        return 'CR2 Automatic'

    def _process_matching(self, matching, affected_list, affected_match, match_affected):
        unmatched = []
        for affected_index, match_indices in affected_match.items():
            if len(match_indices) == 1:
                submatch = match_indices[0]
                match_affected[submatch] -= 1
                archivable = (match_affected[submatch] == 0)
                if archivable:
                    match_affected[submatch] = -1
                yield affected_list[affected_index], submatch, archivable
            else:
                unmatched.append(affected_list[affected_index])
        matchings = sorted(
            [(matching.matches[index], index, count) for index, count in match_affected.items()],
            key=lambda x: x[1], reverse=True)
        self._manual_file.write(serialize_unhandled(matching.key, unmatched, matchings))
