import json

import pytest
from utils.build_info import UNKNOWN, load_build_info

pytestmark = pytest.mark.unit

ALL_UNKNOWN = {'version': UNKNOWN, 'branch': UNKNOWN, 'commit': UNKNOWN, 'buildTime': UNKNOWN}


def test_missing_file_gives_unknown(tmp_path):
    assert load_build_info(tmp_path / 'build-info.json') == ALL_UNKNOWN


def test_reads_all_values(tmp_path):
    path = tmp_path / 'build-info.json'
    expected = {'version': '1.2.0', 'branch': 'main', 'commit': 'abc123', 'buildTime': '2026-10-23T10:00:00Z'}
    path.write_text(json.dumps(expected))

    assert load_build_info(path) == expected


def test_missing_keys_stay_unknown(tmp_path):
    path = tmp_path / 'build-info.json'
    path.write_text(json.dumps({'version': '1.2.0', 'commit': ''}))

    assert load_build_info(path) == {**ALL_UNKNOWN, 'version': '1.2.0'}


def test_broken_json_gives_unknown(tmp_path):
    path = tmp_path / 'build-info.json'
    path.write_text('{not json')

    assert load_build_info(path) == ALL_UNKNOWN


def test_non_object_json_gives_unknown(tmp_path):
    path = tmp_path / 'build-info.json'
    path.write_text('["1.2.0"]')

    assert load_build_info(path) == ALL_UNKNOWN
