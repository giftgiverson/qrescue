"""
Tests for affected.index
"""
import pytest

import affected.index
import my_env.my_env


# region mocks

@pytest.fixture
def mocker_file_read_lines(mocker):
    """mock opening a file with encoded python data-file with encoded dictionary"""
    mocker.patch.object(my_env.my_env, 'DATA_FOLDER', 'flying_circus/')
    mocked_folder_file_data = \
        mocker.mock_open(
            read_data=
            "{'ext': {-1: 100, 0: 1000, 100: 1, 1000: 2},"
            " 'EXT': {-1: 200, 0: 1000, 200: 2, 1000: 1}, }")
    return mocker.patch('builtins.open', mocked_folder_file_data)


def load_pyon_data_file(f_name):
    """mock loading extension summary objects from file"""
    if f_name == 'ext_vers':
        return {'rtf': ['rtf'], 'fft': ['fft', 'FFT'], 'jpeg': ['jPEG', 'JPEG']}
    if f_name == 'ext_histogram':
        return {'rtf': {0: 13631488, 13631488: 1, 12243: 4, -1: 12243},
                'fft': {0: 197208, 197208: 1, -1: 197208},
                'FFT': {0: 197208, 197208: 1, -1: 197208},
                'jPEG': {0: 125030, 63633: 1, 125030: 1, -1: 63633},
                'JPEG': {0: 125030, 63634: 1, 125030: 1, -1: 63634}}
    assert False


# endregion mocks


# region tests

# pylint: disable=redefined-outer-name
def test_load_pyon_data_file(mocker_file_read_lines):
    """test correct loading of pyon data file"""
    actual = [(e, list(o.items())) for e, o in affected.index.load_pyon_data_file('monty').items()]
    expected = [('ext', [(-1, 100), (0, 1000), (100, 1), (1000, 2)]),
                ('EXT', [(-1, 200), (0, 1000), (200, 2), (1000, 1)])]
    assert expected == actual
    mocker_file_read_lines.assert_called_with('flying_circus/monty.pyon', 'r', encoding='utf8')


def test_index(mocker):
    """test correct affected matching in Index"""
    mocker.patch('affected.index.load_pyon_data_file', side_effect=load_pyon_data_file)
    target = affected.index.Index()
    assert target.total_size == 14452203
    # single name, same letters, single match
    assert target.get_matches('rtf', 13631488) == (1, ['rtf'])
    # single name, different letters, single match
    assert target.get_matches('RTF', 13631488) == (1, ['rtf'])
    # single name, same letters, no match
    assert target.get_matches('rtf', 13631487) == (0, [])
    # multi name, multi match
    assert target.get_matches('fft', 197208) == (2, ['fft', 'FFT'])
    # multi name, different letters, single match
    assert target.get_matches('jpeg', 63633) == (1, ['jPEG'])
    # multi name, different letters, single match
    assert target.get_matches('jpeG', 63634) == (1, ['JPEG'])
    # multi name, different letters, multi match
    assert target.get_matches('jpEG', 125030) == (2, ['jPEG', 'JPEG'])
    # non-existing name
    assert target.get_matches('txt', 125030) == (0, [])

# endregion
