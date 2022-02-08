from matches import update_matched_remove_unmatched, squash_matched
from duplicates import update_and_remove_duplicates


def update(is_last=False):
    from_id = update_matched_remove_unmatched(is_last)
    squash_matched()
    update_and_remove_duplicates(from_id)
    squash_matched()


if __name__ == '__main__':
    # === PHASE 2: Index matching, and remove irrelevant, PhotoRec recovered files
    # Use while PhotoRec is still running, to track status and reduce the total disc space needed for this process
    update()
    # Use if PhotoRec has finished running
    # update(True)

    # === PHASE 3: Recovering single-matched files 'blindly'
    # TODO

    # === PHASE 4: Recovering multi-matched files interactively, by type
    # TODO
    print('Done and done')
