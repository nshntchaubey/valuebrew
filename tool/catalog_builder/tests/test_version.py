from pathlib import Path

import pytest

from tool.catalog_builder.version import VersionError, next_catalog_version


def test_no_existing_file_returns_one(tmp_path: Path):
    assert next_catalog_version(tmp_path / "catalog.json") == 1


def test_existing_version_increments_by_exactly_one(tmp_path: Path):
    path = tmp_path / "catalog.json"
    path.write_text('{"catalog_version": 5}', encoding="utf-8")
    assert next_catalog_version(path) == 6


def test_version_one_increments_to_two(tmp_path: Path):
    path = tmp_path / "catalog.json"
    path.write_text('{"catalog_version": 1}', encoding="utf-8")
    assert next_catalog_version(path) == 2


def test_malformed_json_raises(tmp_path: Path):
    path = tmp_path / "catalog.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(VersionError):
        next_catalog_version(path)


def test_missing_catalog_version_key_raises(tmp_path: Path):
    path = tmp_path / "catalog.json"
    path.write_text('{"other_field": 1}', encoding="utf-8")
    with pytest.raises(VersionError):
        next_catalog_version(path)


def test_non_integer_catalog_version_raises(tmp_path: Path):
    path = tmp_path / "catalog.json"
    path.write_text('{"catalog_version": "five"}', encoding="utf-8")
    with pytest.raises(VersionError):
        next_catalog_version(path)


def test_boolean_catalog_version_raises(tmp_path: Path):
    # bool is a subclass of int in Python -- must not silently accept it.
    path = tmp_path / "catalog.json"
    path.write_text('{"catalog_version": true}', encoding="utf-8")
    with pytest.raises(VersionError):
        next_catalog_version(path)


def test_catalog_version_one_on_disk_increments_to_two(tmp_path: Path):
    path = tmp_path / "catalog.json"
    path.write_text('{"catalog_version": 1}', encoding="utf-8")
    assert next_catalog_version(path) == 2
