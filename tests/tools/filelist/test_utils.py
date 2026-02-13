import pytest

from get_a_grip.core.filelist.utils import compare_filelists


def test_compare_filelists_raises_on_duplicate_in_first_result():
    result1 = {
        "files": [
            {"Filename": "C:/tmp/a.txt", "Size": 1, "Date Modified": "1", "Date Created": "1", "Attributes": 0},
            {"Filename": "C:/tmp/a.txt", "Size": 1, "Date Modified": "1", "Date Created": "1", "Attributes": 0},
        ],
        "dirs": [],
    }
    result2 = {
        "files": [
            {"Filename": "C:/tmp/a.txt", "Size": 1, "Date Modified": "1", "Date Created": "1", "Attributes": 0},
        ],
        "dirs": [],
    }

    with pytest.raises(RuntimeError, match="Duplicate entries detected"):
        compare_filelists(result1, result2, "result1", "result2")


def test_compare_filelists_raises_on_duplicate_in_second_result():
    result1 = {
        "files": [
            {"Filename": "C:/tmp/a.txt", "Size": 1, "Date Modified": "1", "Date Created": "1", "Attributes": 0},
        ],
        "dirs": [],
    }
    result2 = {
        "files": [
            {"Filename": "C:/tmp/a.txt", "Size": 1, "Date Modified": "1", "Date Created": "1", "Attributes": 0},
            {"Filename": "C:/tmp/a.txt", "Size": 1, "Date Modified": "1", "Date Created": "1", "Attributes": 0},
        ],
        "dirs": [],
    }

    with pytest.raises(RuntimeError, match="Duplicate entries detected"):
        compare_filelists(result1, result2, "result1", "result2")

