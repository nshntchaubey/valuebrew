import hashlib

import pytest

from tool.ksbcl_pricing_pipeline.classification_config import (
    ClassificationConfigError,
    load_classification_config,
)

VALID_YAML = """\
style_keywords:
  - beer
  - lager
brand_names:
  - Kingfisher
exclusion_terms:
  - whisky
"""


def _write(tmp_path, content, name="beer_classification.yaml"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_valid_config_loads_and_preserves_declaration_order(tmp_path):
    path = _write(tmp_path, VALID_YAML)
    config = load_classification_config(path)
    assert config.style_keywords == ["beer", "lager"]
    assert config.brand_names == ["Kingfisher"]
    assert config.exclusion_terms == ["whisky"]


def test_config_version_is_first_12_hex_of_sha256_of_raw_bytes(tmp_path):
    path = _write(tmp_path, VALID_YAML)
    config = load_classification_config(path)
    expected = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    assert config.config_version == expected
    assert len(config.config_version) == 12


def test_missing_file_raises(tmp_path):
    with pytest.raises(ClassificationConfigError):
        load_classification_config(tmp_path / "does_not_exist.yaml")


def test_empty_file_raises(tmp_path):
    path = _write(tmp_path, "")
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_malformed_yaml_raises(tmp_path):
    path = _write(tmp_path, "style_keywords: [unclosed")
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_missing_required_key_raises(tmp_path):
    path = _write(tmp_path, "style_keywords:\n  - beer\nbrand_names:\n  - Kingfisher\n")
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_unsupported_extra_key_raises(tmp_path):
    path = _write(
        tmp_path,
        VALID_YAML + "version: 1\n",
    )
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_non_list_value_raises(tmp_path):
    path = _write(
        tmp_path,
        "style_keywords: beer\nbrand_names: []\nexclusion_terms: []\n",
    )
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_nested_entry_raises(tmp_path):
    path = _write(
        tmp_path,
        "style_keywords:\n  - beer\nbrand_names:\n  - name: Kingfisher\nexclusion_terms: []\n",
    )
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_empty_style_keywords_raises(tmp_path):
    path = _write(
        tmp_path,
        "style_keywords: []\nbrand_names:\n  - Kingfisher\nexclusion_terms: []\n",
    )
    with pytest.raises(ClassificationConfigError):
        load_classification_config(path)


def test_empty_brand_names_and_exclusion_terms_are_allowed(tmp_path):
    path = _write(
        tmp_path,
        "style_keywords:\n  - beer\nbrand_names: []\nexclusion_terms: []\n",
    )
    config = load_classification_config(path)
    assert config.brand_names == []
    assert config.exclusion_terms == []
