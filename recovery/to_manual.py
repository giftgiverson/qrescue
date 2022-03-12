"""
Convert directly to manual matching
"""
import recovery.timestamp


class ToManualAutoHandler(recovery.timestamp.TimestampAutoHandler):
    """handle conversion to manual matches scanning"""
    @staticmethod
    def can_handle(match):
        """can handle CR2 matches"""
        return True # any(match.key.startswith(ext) for ext in ['m4a', 'mov', 'mp3', 'pdf'])

    def _get_timestamp(self, path):
        """returns non-matching timestamps"""
        return 100 if path.lower().startswith('f:') else 0

    @staticmethod
    def get_type():
        """handler type"""
        return 'To-Manual Automatic'
