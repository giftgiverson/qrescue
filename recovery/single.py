"""
Single-match handler
"""


class SingleHandler:
    """handle single matches recovery"""
    @staticmethod
    def can_handle(match):
        """can handle single matches"""
        return len(match.matches) == 1

    @staticmethod
    def handle(_, affected_list):
        """handle single affected file"""
        if len(affected_list) != 1:
            print(f'EXPECTED SINGLE MATCH, FOUND: {affected_list}')
            return []
        if affected_list[0].is_matched:
            print(f'ALREADY RECOVERED: {affected_list[0]}')
            return []
        return [(affected_list[0], 0)]

    @staticmethod
    def get_type():
        """handler type"""
        return 'Single'
