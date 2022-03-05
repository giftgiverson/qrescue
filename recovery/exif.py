"""
Getting picture-taken date from EXIF
Based on:
 https://orthallelous.wordpress.com/2015/04/19/extracting-date-and-time-from-images-with-python/
"""
from PIL import Image
import os
import datetime
import time
import recovery.timestamp


def get_exif_timestamp_string(path):
    img = Image.open(path) if os.path.exists(path) else None
    exif = img.getexif() if img else None
    if not exif:
        return None
    for tag in [36867, 36868, 306]:
        if tag in exif:
            return exif[tag]
    return None


class ExifAutoHandler(recovery.timestamp.TimestampAutoHandler):
    """handle EXIF matches scanning"""
    @staticmethod
    def can_handle(match):
        """can handle CR2 matches"""
        return any(match.key.startswith(ext) for ext in ['jpg', 'gif', 'png'])

    def _get_timestamp(self, path):
        """returns 'picture taken' timestamp read from CR2 header"""
        str_timestamp = get_exif_timestamp_string(path)
        if not str_timestamp:
            str_timestamp = '1974:08:13 17:35:00'
        f_date_time_dt = datetime.datetime.strptime(str_timestamp, '%Y:%m:%d %H:%M:%S')
        return time.mktime(f_date_time_dt.timetuple())

    @staticmethod
    def get_type():
        """handler type"""
        return 'EXIF Automatic'
