"""
Getting picture-taken date from CR2
Based on:
 https://stackoverflow.com/questions/3696642/reading-a-cr2-raw-canon-image-header-using-python
"""
import struct

recognised_tags = {
    0x0100: 'imageWidth',
    0x0101: 'imageLength',
    0x0102: 'bitsPerSample',
    0x0103: 'compression',
    0x010f: 'make',
    0x0110: 'model',
    0x0111: 'stripOffset',
    0x0112: 'orientation',
    0x0117: 'stripByteCounts',
    0x011a: 'xResolution',
    0x011b: 'yResolution',
    0x0128: 'resolutionUnit',
    0x0132: 'dateTime',
    0x8769: 'EXIF',
    0x8825: 'GPS data'}


def _get_header_from_cr2(buffer):
    # Unpack the header into a tuple
    header = struct.unpack_from('HHLHBBL', buffer)

    print(f'\nbyte_order = 0x{header[0]:04X}')
    print(f'tiff_magic_word = {header[1]:d}')
    print(f'tiff_offset = 0x{header[2]:08X}')
    print(f'cr2_magic_word = {header[3]:d}')
    print(f'cr2_major_version = {header[4]:d}')
    print(f'cr2_minor_version = {header[5]:d}')
    print(f'raw_ifd_offset = 0x{header[6]:08X}\n')

    return header


def _find_date_time_offset_from_cr2(buffer, ifd_offset, endian_flag):
    # Read the number of entries in IFD #0
    (num_of_entries,) = struct.unpack_from(endian_flag+'H', buffer, ifd_offset)
    print(f'Image File Directory #0 contains {num_of_entries:d} entries\n')

    # Work out where the date time is stored
    datetime_offset = -1

    # Go through all the entries looking for the datetime field
    print(' id  | type |  number  |  value   ')
    for entry_num in range(0, num_of_entries):

        # Grab this IFD entry
        (tag_id, tag_type, num_of_value, value) =\
            struct.unpack_from(endian_flag+'HHLL', buffer, ifd_offset+2+entry_num*12)

        # Print out the entry for information
        print(f'{tag_id:04X} | {tag_type:04X} | {num_of_value:08X} | {value:08X} ', end=' ')
        if tag_id in recognised_tags:
            print(recognised_tags[tag_id])

        # If this is the datetime one we're looking for, make a note of the offset
        if tag_id == 0x0132:
            assert tag_type == 2
            assert num_of_value == 20
            datetime_offset = value

    return datetime_offset


def _get_cr2_datetime_offset(path):
    with open(path, 'rb') as cr2_file:
        buffer = cr2_file.read(1024)
        # (byte_order, tiff_magic_word, tiff_offset, cr2_magic_word, cr2_major_version,
        #  cr2_minor_version, raw_ifd_offset) = _get_header_from_cr2(buffer)
        (byte_order, _, _, _, _, _, _) = _get_header_from_cr2(buffer)
        endian_flag = '>' if byte_order == 0x4D4D else ('<' if byte_order == 0x4949 else '@')
        datetime_offset = _find_date_time_offset_from_cr2(buffer, 0x10, endian_flag)
        datetime_b_string = struct.unpack_from(20 * 's', buffer, datetime_offset)
        datetime_string = ''.join([b.decode('utf-8') for b in datetime_b_string][:-1])
        print(f'\nDatetime: {datetime_string}\n')
        return datetime_string


def get_cr2_datetime_offsets(matching):
    """
    :param matching: single/multi matching item
    :return: each inner match's time string as read from the CR2 file
    """
    return [_get_cr2_datetime_offset(match.path) for match in matching.matches]
