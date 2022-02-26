"""
Implement interactive manual matching
"""
import os.path
import re
import my_env
import affected
import matches
from my_misc import static_vars

RESCUED_OFFSET = 2
RESCUED_PART_SIZE = 3
CANDIDATE_PART_SIZE = 4
MANUAL_CSV = 'manual_match.csv'


def _part_groups(parts, offset, part_size, part_count):
    return [parts[n * part_size + offset:(n + 1) * part_size + offset] for n in
            range(0, part_count)]


def _part_groups_parse(maker, parts, offset, part_size, part_count):
    return [maker(part) for part in _part_groups(parts, offset, part_size, part_count)]


class Candidate(matches.Recuperated):
    """Recuperated wrapper for tracking manual recovery"""
    @property
    def submatch(self):
        """
        :return: submatch ID
        """
        return self._submatch

    @property
    def match_count(self):
        """
        :return: number of matches
        """
        return self._match_count

    @property
    def manual_path(self):
        """manual path"""
        return  self._manual_path

    @manual_path.setter
    def manual_path(self, path):
        self._manual_path = path

    def __init__(self, detail):
        super().__init__(detail[:2])
        self._submatch = int(detail[2])
        self._match_count = int(detail[3])
        if self._match_count < 0:
            self._path = my_env.rescued_to_archived(self._path)
        self._manual_path = None

    def serialize(self):
        """make a list of the internal properties"""
        return [self._id, self._name, str(self._submatch), str(self.match_count)]

    def __repr__(self):
        return f'___{"C" if self.match_count > 0 else "Z"}[{self.submatch}]_[{self.match_count}]'


class Rescued(affected.AffectedFile):
    """AffectedFile wrapper for tracking manual recovery"""

    @property
    def status(self):
        """
        :return: (string) the file's match-status code
        """
        return self._status

    @property
    def new_status(self):
        """
        :return: new status given manually
        """
        return self._new_status

    @new_status.setter
    def new_status(self, new_status):
        """
        Set manual status
        :param new_status: manual status
        """
        if self.needs_match and self._current:
            self._new_status = new_status
            return
        print('WARNING: Cannot change status of rescued items not current, nor needing a match')

    @property
    def is_current(self):
        """
        :return: flags this object as participating in current handling of affected files
        """
        return self._current

    @is_current.setter
    def is_current(self, current):
        """
        Flag this object's participation in current handling of affected files
        :param current: (bool) participation flag
        """
        self._current = current

    @property
    def is_matched(self):
        """
        :return: flag this object as having a match
        """
        return re.match(r'^\d+$', self._status)

    def __init__(self, detail, ext, folders):
        super().__init__(', '.join(detail[:2] + [ext, '0', '0', detail[2]]), folders)
        self._new_status = self.status
        self._current = False

    def apply_new_status(self):
        """Set the manual status as the actual status"""
        if self._status == self._new_status:
            return False
        self._status = self._new_status
        return True


class ManualSelection:
    """Manage a keyed manual selection"""

    @property
    def key(self):
        """
        :return: selection key
        """
        return self._key

    @property
    def can_match(self):
        """
        :return: flag this instance as possible for a manual match
        """
        return self._can_match

    def __init__(self, line, folders):
        parts = [p.strip() for p in line.split(',')]
        self._key = parts[0]
        self._ext = self.key.split('.')[0]
        rescued_count = int(parts[1])
        self._rescued = _part_groups_parse(
            lambda x: Rescued(x, self._ext, folders),
            parts, RESCUED_OFFSET, RESCUED_PART_SIZE, rescued_count)
        self._can_match = any(rescued.needs_match for rescued in self._rescued)
        match_offset = RESCUED_OFFSET + rescued_count * 3 + 1
        match_count = int(parts[match_offset - 1])
        self._candidates = _part_groups_parse(
            Candidate, parts, match_offset, CANDIDATE_PART_SIZE, match_count)
        self._current_paths = []

    def serialize(self):
        """serialize this object as a CSV line"""
        return ', '.join(
            [self._key, str(len(self._rescued))] +
            [part for item in self._rescued for part in [item.status, item.folder_key, item.name]] +
            [str(len(self._candidates))] +
            [part for item in self._candidates for part in item.serialize()]
        )

    def __repr__(self):
        return self.serialize()

    def show_candidates(self):
        """Copy candidate files to manual folder"""
        for candidate in self._candidates:
            candidate.manual_path =\
                my_env.copy_to_manual_folder_as(
                    candidate.path,
                    '.'.join([str(candidate), self._ext]))

    def show_neighbors(self):
        """Copy neighboring files to manual folder"""
        neighbors = {}
        for i, item in enumerate(self._rescued):
            for neighbor in my_env.neighbor_names(item.path):
                if neighbor not in neighbors:
                    neighbors[neighbor] = []
                neighbors[neighbor].append(str(i))
        for neighbor, rescued_indices in neighbors.items():
            my_env.copy_to_manual_folder_as(
                neighbor,
                f'___N[{",".join(rescued_indices)}]_' + os.path.basename(neighbor))

    def _show_summary(self):
        """Present status and command options"""
        print('\n==========\nCandidates:')
        for item in self._candidates:
            print(f'[{item.submatch}] [{item}]')
        print('----------\nRescued:')
        for i, item in enumerate(self._rescued):
            print(f'[{i}][{item.new_status if item.is_current else "!"}] {item.path}')
        print('----------\nCommand Options:')
        print('<i>:<j> - mark candidate item <i> as matching rescued item <j>')
        print('<f>?<i> - run compare tool with candidate items <f> and <i>')
        print('Drop:<j> - mark rescued item <j> as dropped from matching')
        print('Reset - Remove manual matches')
        print('Next - Update and report manual matches')
        print('Escape - Terminate manual process\n')

    def collect_decisions(self, affected_list):
        """Collect manual decisions"""
        self._current_paths = [item.path for item in affected_list]
        for rescued in self._rescued:
            rescued.is_current = (rescued.path in self._current_paths)
        is_aborted = self._interactive_match()
        return is_aborted, list(self._translate_matched(affected_list))

    def _interactive_match(self):
        show_again = True
        while True:
            if show_again:
                self._show_summary()
            else:
                show_again = True
            command = input('> ').lower()
            if command.startswith('escape'):
                return True
            if command.startswith('next'):
                break
            if command.startswith('reset'):
                for item in self._rescued:
                    item.new_status = -1
                continue
            drop = re.search(r'drop:(\d+)', command)
            if drop:
                selected_rescued = int(drop.groups()[0])
                self._rescued[selected_rescued].new_status = 'D'
                continue
            decision = re.search(r'(\d+):(\d+)', command)
            if decision:
                selected_candidate, selected_rescued = decision.groups()
                self._rescued[int(selected_rescued)].new_status = selected_candidate
                continue
            comparison = re.search(r'(\d+)\?(\d+)', command)
            if comparison:
                path1, path2 = [self._candidates[int(i)].manual_path for i in comparison.groups()]
                my_env.show_comparison(path1, path2)
                show_again = False
                continue
            print('Unable to handle command: ' + command)
        return False

    def _handle_new_matched(self):
        rescued_by_candidate = {}
        for rescued in self._rescued:
            if rescued.apply_new_status() and rescued.is_matched:
                if rescued.status not in rescued_by_candidate:
                    rescued_by_candidate[rescued.status] = []
                rescued_by_candidate[rescued.status].append(rescued)
        for status, rescued in rescued_by_candidate.items():
            for i, item in enumerate(rescued):
                yield item, status, i == (len(rescued) - 1)

    def _translate_matched(self, affected_list):
        for match, submatch, archivable in self._handle_new_matched():
            yield affected_list[self._current_paths.index(match.path)], int(submatch), archivable


@static_vars(manual={})
def load_manual(refresh=False):
    """
    Load manual recovery data
    :param refresh: should the files be re-read from file
    :return: Keyed dictionary of manual recoveries
    """
    if refresh or not load_manual.manual:
        folders = affected.folders.load_folders()
        read_manual = {}
        with my_env.data_file(MANUAL_CSV) as file:
            for line in file:
                item = ManualSelection(line, folders)
                read_manual[item.key] = item
        load_manual.manual = read_manual
    return load_manual.manual


def update_manual(manual):
    """
    Update manual recovery data (backing up previous version)
    :param manual: updated ManualSelection list
    """
    my_env.data_backup(MANUAL_CSV)
    with my_env.data_file(MANUAL_CSV, 'w') as file:
        for item in manual.values():
            file.write(item.serialize() + '\n')
    load_manual.manual = {}


class ManualHandler:
    """handle manual matches scanning"""

    def __init__(self):
        self._manual = None
        self._aborted = False

    def __enter__(self):
        self._manual = load_manual(True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        update_manual(self._manual)

    def can_handle(self, match):
        """can handle manual matches"""
        return\
            not self._aborted \
            and match.key in self._manual \
            and self._manual[match.key].can_match

    def handle(self, matching, affected_list):
        """handle manual match scanning"""
        if len(affected_list) == 0:
            return []
        selection = self._manual[matching.key]
        my_env.clear_manual_folder()
        selection.show_candidates()
        selection.show_neighbors()
        self._aborted, decisions = selection.collect_decisions(affected_list)
        return decisions

    @staticmethod
    def get_type():
        """return handler type"""
        return 'Manual handler'
