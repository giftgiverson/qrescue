"""
Entry point for QRescue automation
"""

from matches import update_matched_remove_unmatched, squash_matched
from duplicates import update_and_remove_duplicates
# pylint: disable=unused-import
from recovery import Recovery, SingleHandler, Cr2AutoHandler, ManualHandler, ExifAutoHandler,\
    ToManualAutoHandler


def update(is_last=False):
    """
    Update match indices, remove irrelevant files
    :param is_last: (default='False') Should the last available folder be used
    """
    from_id = update_matched_remove_unmatched(is_last)
    squash_matched()
    update_and_remove_duplicates(from_id)
    squash_matched()


if __name__ == '__main__':
    # === PHASE 2: Index matching, and remove irrelevant, PhotoRec recovered files
    # Use while PhotoRec is still running, to track status
    # and reduce the total disc space needed for this process
    # update()

    # Use if PhotoRec has finished running
    # update(True)

    recovery = Recovery()
    # === PHASE 3: Recovering single-matched files 'blindly'
    # recovery.mark_unrecoverable()
    # recovery.recover_single_matched(SingleHandler())

    # === PHASE 4: Recovering multi-matched files interactively, by type
    # == 4.1 CR2
    # with Cr2AutoHandler() as handler:
    #     recovery.recover_multi_matched(handler)
    # == 4.2 EXIF
    # with ExifAutoHandler() as handler:
    #     recovery.recover_multi_matched(handler)
    # == 4.9 Rest to manual
    # with ToManualAutoHandler() as handler:
    #     recovery.recover_multi_matched(handler)
    # pylint: disable=fixme
    # TODO

    # === PHASE 5: Recovering manually-matched files
    with ManualHandler() as handler:
        recovery.recover_multi_matched(handler)
    print('Done and done')
