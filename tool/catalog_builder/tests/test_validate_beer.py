from pathlib import Path

import yaml

from tool.catalog_builder.validate_beer import compute_invalid_beer_keys, validate_beer_file

_STYLES = [{"style_key": "lager", "name": "Lager", "description": "Crisp"}]

_ABV_BLOCK = {
    "value": 4.8,
    "source_type": "manufacturer",
    "source_name": "United Breweries official product page",
    "observed_at": "2026-08-13",
    "observed_by": "founder",
}

_SINGLE_SKU_BEER = {
    "beer_key": "kingfisher_premium",
    "canonical_product_ids": ["CP0000002"],
    "name": "Kingfisher Premium",
    "brewery": "United Breweries",
    "style": "lager",
    "abv": _ABV_BLOCK,
    "calories_per_100ml": _ABV_BLOCK,
}


def _setup(tmp_path: Path):
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    styles_path = enrichment_dir / "styles.yaml"
    styles_path.write_text(yaml.safe_dump(_STYLES), encoding="utf-8")
    return enrichment_dir, beers_dir, styles_path


def _write_beer(beers_dir: Path, filename: str, data: dict) -> Path:
    path = beers_dir / filename
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Passing cases
# ---------------------------------------------------------------------------


def test_single_sku_beer_passes(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", _SINGLE_SKU_BEER)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is True
    assert result.issues == []
    assert result.beer.canonical_product_ids == ["CP0000002"]


def test_multi_sku_beer_passes(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, canonical_product_ids=["CP0000002", "CP0000003", "CP0000004"])
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is True
    assert result.beer.canonical_product_ids == ["CP0000002", "CP0000003", "CP0000004"]


def test_unknown_style_and_abv_are_not_rejected(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, style="unknown", abv="unknown")
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is True
    assert result.beer.style is None
    assert result.beer.abv is None


def test_valid_sku_override_passes(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(
        _SINGLE_SKU_BEER,
        canonical_product_ids=["CP0000002", "CP0000003"],
        skus={"CP0000003": _ABV_BLOCK},
    )
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is True


# ---------------------------------------------------------------------------
# Rejections — single-file structural
# ---------------------------------------------------------------------------


def test_invalid_style_reference_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, style="nonexistent_style")
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert result.beer is None
    assert result.issues[0].reason_code == "unresolved_style_reference"


def test_missing_abv_key_entirely_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = {k: v for k, v in _SINGLE_SKU_BEER.items() if k != "abv"}
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert result.issues[0].reason_code == "missing_required_keys"


def test_missing_brewery_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = {k: v for k, v in _SINGLE_SKU_BEER.items() if k != "brewery"}
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert result.issues[0].reason_code == "missing_required_keys"


def test_malformed_yaml_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer_path = beers_dir / "broken.yaml"
    beer_path.write_text("beer_key: [unterminated", encoding="utf-8")

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert result.beer is None
    assert result.issues[0].reason_code == "unparseable_yaml"


def test_file_not_found(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    result = validate_beer_file(beers_dir / "nope.yaml", styles_path=styles_path, beers_dir=beers_dir)
    assert result.valid is False
    assert result.issues[0].reason_code == "file_not_found"


def test_duplicate_canonical_product_id_within_one_beer_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, canonical_product_ids=["CP0000002", "CP0000002"])
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert any(i.reason_code == "duplicate_canonical_product_id_within_beer" for i in result.issues)


def test_sku_override_referencing_id_not_in_beer_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, skus={"CP0000099": _ABV_BLOCK})
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert any(i.reason_code == "sku_override_not_in_canonical_product_ids" for i in result.issues)


# ---------------------------------------------------------------------------
# Rejections — repository-wide
# ---------------------------------------------------------------------------


def test_duplicate_beer_key_flagged_against_a_stray_mismatched_file(tmp_path: Path):
    # Filesystem uniqueness plus the filename==beer_key rule together
    # mean two independently-*valid* files can never share a beer_key.
    # The real, catchable case this check exists for is a stray,
    # internally-inconsistent file (its own filename doesn't match its
    # content — it would fail validation if checked on its own) whose
    # raw beer_key nonetheless collides with a real, valid file's.
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_beer(beers_dir, "old_draft.yaml", dict(_SINGLE_SKU_BEER, canonical_product_ids=["CP0000099"]))
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", _SINGLE_SKU_BEER)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert any(i.reason_code == "duplicate_beer_key" for i in result.issues)


def test_canonical_product_id_claimed_by_two_different_beers_fails(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_beer(beers_dir, "other_beer.yaml", dict(_SINGLE_SKU_BEER, beer_key="other_beer"))
    beer_path = _write_beer(beers_dir, "kingfisher_premium.yaml", _SINGLE_SKU_BEER)

    result = validate_beer_file(beer_path, styles_path=styles_path, beers_dir=beers_dir)

    assert result.valid is False
    assert any(i.reason_code == "canonical_product_id_claimed_by_another_beer" for i in result.issues)


# ---------------------------------------------------------------------------
# compute_invalid_beer_keys -- parity with validate_beer_file, per fixture
#
# The O(n) rewrite of compute_invalid_beer_keys must produce exactly the
# same invalid/valid verdict validate_beer_file already produces for
# every one of the scenarios above -- reusing those exact fixtures
# rather than inventing new ones, so "same invalid set as before" is
# checked against the same real cases already proven correct.
# ---------------------------------------------------------------------------


def test_compute_invalid_beer_keys_single_sku_beer_is_not_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_beer(beers_dir, "kingfisher_premium.yaml", _SINGLE_SKU_BEER)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == set()


def test_compute_invalid_beer_keys_multi_sku_beer_is_not_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, canonical_product_ids=["CP0000002", "CP0000003", "CP0000004"])
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == set()


def test_compute_invalid_beer_keys_unknown_style_and_abv_are_not_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, style="unknown", abv="unknown")
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == set()


def test_compute_invalid_beer_keys_valid_sku_override_is_not_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(
        _SINGLE_SKU_BEER,
        canonical_product_ids=["CP0000002", "CP0000003"],
        skus={"CP0000003": _ABV_BLOCK},
    )
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == set()


def test_compute_invalid_beer_keys_invalid_style_reference_is_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, style="nonexistent_style")
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == {"kingfisher_premium"}


def test_compute_invalid_beer_keys_missing_abv_key_is_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = {k: v for k, v in _SINGLE_SKU_BEER.items() if k != "abv"}
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == {"kingfisher_premium"}


def test_compute_invalid_beer_keys_missing_brewery_is_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = {k: v for k, v in _SINGLE_SKU_BEER.items() if k != "brewery"}
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == {"kingfisher_premium"}


def test_compute_invalid_beer_keys_malformed_yaml_is_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    (beers_dir / "broken.yaml").write_text("beer_key: [unterminated", encoding="utf-8")

    assert compute_invalid_beer_keys(beers_dir, styles_path) == {"broken"}


def test_compute_invalid_beer_keys_duplicate_canonical_product_id_within_beer_is_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, canonical_product_ids=["CP0000002", "CP0000002"])
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == {"kingfisher_premium"}


def test_compute_invalid_beer_keys_sku_override_referencing_id_not_in_beer_is_invalid(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    beer = dict(_SINGLE_SKU_BEER, skus={"CP0000099": _ABV_BLOCK})
    _write_beer(beers_dir, "kingfisher_premium.yaml", beer)

    assert compute_invalid_beer_keys(beers_dir, styles_path) == {"kingfisher_premium"}


def test_compute_invalid_beer_keys_flags_the_valid_file_a_stray_mismatched_file_collides_with(tmp_path: Path):
    # Mirrors test_duplicate_beer_key_flagged_against_a_stray_mismatched_file:
    # old_draft.yaml is itself internally inconsistent (its own filename
    # doesn't match its content, so it's invalid on its own merits too),
    # but the real, valid kingfisher_premium.yaml must ALSO be flagged,
    # since another real file's raw beer_key collides with its own.
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_beer(beers_dir, "old_draft.yaml", dict(_SINGLE_SKU_BEER, canonical_product_ids=["CP0000099"]))
    _write_beer(beers_dir, "kingfisher_premium.yaml", _SINGLE_SKU_BEER)

    invalid = compute_invalid_beer_keys(beers_dir, styles_path)

    assert "kingfisher_premium" in invalid
    assert "old_draft" in invalid  # invalid on its own terms too (beer_key != filename)


def test_compute_invalid_beer_keys_flags_both_beers_sharing_a_canonical_product_id(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_beer(beers_dir, "other_beer.yaml", dict(_SINGLE_SKU_BEER, beer_key="other_beer"))
    _write_beer(beers_dir, "kingfisher_premium.yaml", _SINGLE_SKU_BEER)

    invalid = compute_invalid_beer_keys(beers_dir, styles_path)

    assert "kingfisher_premium" in invalid
    assert "other_beer" in invalid


def test_compute_invalid_beer_keys_missing_beers_dir_returns_empty_set(tmp_path: Path):
    assert compute_invalid_beer_keys(tmp_path / "does_not_exist", tmp_path / "styles.yaml") == set()


def test_compute_invalid_beer_keys_broken_styles_yaml_invalidates_every_beer(tmp_path: Path):
    enrichment_dir = tmp_path / "enrichment"
    beers_dir = enrichment_dir / "beers"
    beers_dir.mkdir(parents=True)
    styles_path = enrichment_dir / "styles.yaml"
    styles_path.write_text("not: [a, valid, styles, list", encoding="utf-8")  # malformed YAML

    _write_beer(beers_dir, "kingfisher_premium.yaml", dict(_SINGLE_SKU_BEER, style="unknown", abv="unknown"))
    _write_beer(
        beers_dir,
        "tuborg_green.yaml",
        dict(_SINGLE_SKU_BEER, beer_key="tuborg_green", canonical_product_ids=["CP0000059"], style="unknown", abv="unknown"),
    )

    invalid = compute_invalid_beer_keys(beers_dir, styles_path)

    assert invalid == {"kingfisher_premium", "tuborg_green"}


# ---------------------------------------------------------------------------
# compute_invalid_beer_keys -- large synthetic repository, single-pass proof
#
# Not a timing test: proves the O(n) claim structurally, by counting
# real filesystem reads. The old implementation (validate_beer_file
# called once per beer, each call re-scanning every *other* file) would
# perform roughly n^2 reads here; the fix performs exactly n.
# ---------------------------------------------------------------------------


def _write_synthetic_repository(beers_dir: Path, count: int) -> None:
    for i in range(count):
        beer_key = f"beer_{i:04d}"
        _write_beer(
            beers_dir,
            f"{beer_key}.yaml",
            dict(
                _SINGLE_SKU_BEER,
                beer_key=beer_key,
                canonical_product_ids=[f"CP{i:07d}"],
            ),
        )


def test_compute_invalid_beer_keys_large_repository_produces_no_false_positives(tmp_path: Path):
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_synthetic_repository(beers_dir, 150)

    invalid = compute_invalid_beer_keys(beers_dir, styles_path)

    assert invalid == set()


def test_compute_invalid_beer_keys_large_repository_reads_each_file_exactly_once(tmp_path: Path, monkeypatch):
    """Structural proof of single-pass behavior, not a timing assertion.
    Counts real Path.read_text calls against beer files while computing
    invalid keys over a 150-beer synthetic repository. The old
    implementation (validate_beer_file looped once per beer, each call
    rescanning every other file via _check_against_repository) would
    perform on the order of n^2 (~22,000+) reads here; this asserts the
    count stays linear in n, which n^2 behavior could never satisfy at
    this size."""
    _, beers_dir, styles_path = _setup(tmp_path)
    beer_count = 150
    _write_synthetic_repository(beers_dir, beer_count)

    real_read_text = Path.read_text
    read_calls = {"count": 0}

    def counting_read_text(self, *args, **kwargs):
        if self.suffix == ".yaml" and self.parent == beers_dir:
            read_calls["count"] += 1
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counting_read_text)

    invalid = compute_invalid_beer_keys(beers_dir, styles_path)

    assert invalid == set()
    # Exactly one read per beer file in the single-pass implementation.
    # A quadratic implementation would need beer_count * (beer_count - 1)
    # extra reads on top of this (~22,000 for 150 files) -- nowhere close
    # to satisfying "fewer than 3x the file count".
    assert read_calls["count"] == beer_count
    assert read_calls["count"] < beer_count * 3


def test_compute_invalid_beer_keys_large_repository_with_one_real_conflict(tmp_path: Path):
    # A single genuine cross-file conflict must still be found correctly
    # even at scale, and must not spuriously flag any of the other,
    # unrelated beers.
    _, beers_dir, styles_path = _setup(tmp_path)
    _write_synthetic_repository(beers_dir, 150)
    # beer_0075 and beer_0100 both claim CP0000075.
    conflicting = dict(_SINGLE_SKU_BEER, beer_key="beer_0100", canonical_product_ids=["CP0000075"])
    _write_beer(beers_dir, "beer_0100.yaml", conflicting)

    invalid = compute_invalid_beer_keys(beers_dir, styles_path)

    assert invalid == {"beer_0075", "beer_0100"}
