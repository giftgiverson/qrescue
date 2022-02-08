import affected
from matches import update_matched_remove_unmatched, squash_matched
from duplicates import update_and_remove_duplicates


def update(is_last=False):
    from_id = update_matched_remove_unmatched(is_last)
    squash_matched()
    update_and_remove_duplicates(from_id)
    squash_matched()


if __name__ == '__main__':
    update()
    print('Done and done')
