"""
Getting picture-taken date from CR2
Based on:
 https://stackoverflow.com/questions/3696642/reading-a-cr2-raw-canon-image-header-using-python
"""
import struct
import datetime
import time
import recovery.timestamp

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


def get_cr2_datetime_string(path):
    """returns 'picture taken' date-time string read from CR2 header"""
    with open(path, 'rb') as cr2_file:
        buffer = cr2_file.read(1024)
        (byte_order, _, _, _, _, _, _) = _get_header_from_cr2(buffer)
        endian_flag = '>' if byte_order == 0x4D4D else ('<' if byte_order == 0x4949 else '@')
        datetime_offset = _find_date_time_offset_from_cr2(buffer, 0x10, endian_flag)
        datetime_b_string = struct.unpack_from(20 * 's', buffer, datetime_offset)
        return ''.join([b.decode('utf-8') for b in datetime_b_string][:-1])


class Cr2AutoHandler(recovery.timestamp.TimestampAutoHandler):
    """handle CR2 matches scanning"""
    @staticmethod
    def can_handle(match):
        """can handle CR2 matches"""
        return match.key.startswith('cr2')

    def _get_timestamp(self, path):
        """returns 'picture taken' timestamp read from CR2 header"""
        f_date_time_dt = datetime.datetime.strptime(
            get_cr2_datetime_string(path), '%Y:%m:%d %H:%M:%S')
        return time.mktime(f_date_time_dt.timetuple())

    @staticmethod
    def get_type():
        """handler type"""
        return 'CR2 Automatic'
