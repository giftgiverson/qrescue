"""
Getting picture-taken date from CR2
Based on:
 https://stackoverflow.com/questions/3696642/reading-a-cr2-raw-canon-image-header-using-python
"""
import struct
import datetime
import time
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


class Cr2ScanHandler:
    """handle CR2 matches scanning"""

    @staticmethod
    def can_handle(match):
        """can handle CR2 matches"""
        return match.key.startswith('cr2')

    @staticmethod
    def handle(matching, affected_list):
        """handle CR2 match scanning"""
        if len(affected_list) == 0:
            return []
        matched = [(i, get_cr2_datetime_offset(match.path))
                   for i, match in enumerate(matching.matches)]
        neighborhood = [(i, my_env.neighbor_modified_limits(affected.path))
                        for i, affected in enumerate(affected_list)]
        affected_match = {i: [] for i in range(0, len(affected_list))}
        Cr2ScanHandler.handle_couples(matched, neighborhood, affected_match)
        # singe/none handling?
        return [[affected_list[affected_index], matching.matches[match_indices[0]]]
                for affected_index, match_indices in affected_match.items()
                if len(match_indices) == 1]

    @staticmethod
    def get_type():
        """handler type"""
        return 'CR2'

    @staticmethod
    def handle_couples(matched, neighborhood, affected_match):
        """tries to match affected by picture-time-taken range read from its neighbors"""
        for affected_index, neighbors in neighborhood:
            edges = [get_cr2_datetime_offset(path) for path in neighbors]
            for match_index, match_cr2_timestamp in matched:
                if edges[0] <= match_cr2_timestamp <= edges[1]:
                    affected_match[affected_index].append(match_index)
