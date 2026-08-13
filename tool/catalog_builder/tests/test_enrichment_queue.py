from pathlib import Path

from tool.catalog_builder.contamination_filter import load_default_exclusion_terms
from tool.catalog_builder.enrichment_queue import (
    build_enrichment_queue,
    display_group_key,
)
from tool.catalog_builder.models import Candidate, EnrichmentBeer, RejectedCandidateFile, RejectedEnrichmentFile
from tool.catalog_builder.schema_validate import validate_candidates_directory, validate_enrichment_repository

_TERMS = ["whisky", "whiskey", "rum", "brandy", "vodka", "gin"]


def _candidate(cpid: str, name: str = "Some Beer") -> Candidate:
    return Candidate(
        canonical_product_id=cpid,
        item_name_raw=name,
        display_name=name,
        suggested_beer_key=None,
        name=None,
        brewery=None,
        style=None,
        abv=None,
        is_craft=None,
        images=[],
    )


def _beer(beer_key: str, canonical_product_ids) -> EnrichmentBeer:
    return EnrichmentBeer(
        beer_key=beer_key,
        canonical_product_ids=canonical_product_ids,
        name="X",
        brewery="Y",
        style=None,
        abv=None,
        calories_per_100ml=None,
    )


def _build(candidates, rejected_candidate_files=(), beers=(), *, rejected_beer_files=(), container_type_by_id=None):
    return build_enrichment_queue(
        candidates,
        list(rejected_candidate_files),
        list(beers),
        _TERMS,
        rejected_beer_files=list(rejected_beer_files),
        container_type_by_id=container_type_by_id or {},
    )


# ---------------------------------------------------------------------------
# display_group_key
# ---------------------------------------------------------------------------


def test_strips_can_and_size_suffix():
    assert display_group_key("kingfisher premium lager beer-can 330ml") == "kingfisher premium lager beer"


def test_strips_bare_size_suffix_no_can():
    assert display_group_key("kingfisher premium lager beer 650ml") == "kingfisher premium lager beer"


def test_strips_size_with_space_before_ml():
    assert display_group_key("king fisher premium lager beer 330 ml") == "king fisher premium lager beer"


def test_strips_multiplier_suffix():
    assert display_group_key("budweiser magnum whiskey 750mlx12btls") == "budweiser magnum whiskey"


def test_known_limitation_different_spelling_does_not_cluster():
    # Documented, not fixed -- "Kingfisher" vs "King Fisher" are
    # genuinely different strings; this heuristic doesn't resolve real
    # data inconsistency, only pack-size suffixes.
    a = display_group_key("kingfisher premium lager beer-can 330ml")
    b = display_group_key("king fisher premium lager beer 330 ml")
    assert a != b


# ---------------------------------------------------------------------------
# Five buckets
# ---------------------------------------------------------------------------


def test_five_buckets_partition_correctly():
    candidates = [
        _candidate("CP0000001", "Already Enriched Beer"),
        _candidate("CP0000002", "Kingfisher Premium Lager Beer-CAN 330ML"),
        _candidate("CP0000003", "Kingfisher Premium Lager Beer 650ML"),  # unknown container
        _candidate("CP0000004", "Some Whiskey Product"),
    ]
    rejected_files = [RejectedCandidateFile(filename="CP0000005.yaml", reason_code="unparseable_yaml", reason_detail="bad")]
    beers = [_beer("already_enriched", ["CP0000001"])]
    container_type_by_id = {"CP0000002": "can", "CP0000003": "unknown"}

    report = _build(candidates, rejected_files, beers, container_type_by_id=container_type_by_id)

    assert report.total_candidates == 5
    assert report.enriched_count == 1
    assert report.contamination_count == 1
    assert report.structurally_blocked_count == 1
    assert report.remaining_count == 1
    assert report.malformed_count == 1


def test_structurally_blocked_entry_carries_container_type_and_reason():
    candidates = [_candidate("CP0000003", "Kingfisher Premium Lager Beer 650ML")]
    report = _build(candidates, container_type_by_id={"CP0000003": "unknown"})
    assert report.structurally_blocked[0].container_type == "unknown"
    assert "unknown" in report.structurally_blocked[0].reason


def test_enriched_entry_carries_beer_key():
    candidates = [_candidate("CP0000001")]
    beers = [_beer("kingfisher_premium", ["CP0000001"])]
    report = _build(candidates, beers=beers)
    assert report.enriched[0].beer_key == "kingfisher_premium"


def test_no_container_type_data_never_blocks_by_default():
    # If the caller doesn't supply container_type data, nothing is
    # structurally blocked on that basis -- absence of data is not
    # treated as a block.
    candidates = [_candidate("CP0000002")]
    report = _build(candidates)
    assert report.structurally_blocked == []
    assert report.remaining_count == 1


def test_bottle_and_can_are_never_structurally_blocked():
    candidates = [_candidate("CP0000002"), _candidate("CP0000003")]
    report = _build(candidates, container_type_by_id={"CP0000002": "can", "CP0000003": "bottle"})
    assert report.structurally_blocked == []
    assert report.remaining_count == 2


# ---------------------------------------------------------------------------
# Display-only grouping
# ---------------------------------------------------------------------------


def test_remaining_grouped_clusters_pack_size_siblings():
    candidates = [
        _candidate("CP0000002", "Kingfisher Premium Lager Beer-CAN 330ML"),
        _candidate("CP0000003", "Kingfisher Premium Lager Beer-CAN 500ML"),
        _candidate("CP0000004", "Tuborg Strong Beer-CAN 500ML"),
    ]
    report = _build(candidates)
    group_keys = {g.display_group_key for g in report.remaining_grouped}
    assert "kingfisher premium lager beer" in group_keys
    kf_group = next(g for g in report.remaining_grouped if g.display_group_key == "kingfisher premium lager beer")
    assert {e.canonical_product_id for e in kf_group.entries} == {"CP0000002", "CP0000003"}


def test_groups_sorted_deterministically():
    candidates = [
        _candidate("CP0000002", "Zebra Lager-CAN 330ML"),
        _candidate("CP0000003", "Alpha Lager-CAN 330ML"),
    ]
    report = _build(candidates)
    keys = [g.display_group_key for g in report.remaining_grouped]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Determinism, malformed/rejected propagation (existing coverage, updated)
# ---------------------------------------------------------------------------


def test_output_is_deterministic_across_calls():
    candidates = [_candidate("CP0000099"), _candidate("CP0000002")]
    first = _build(candidates)
    second = _build(candidates)
    assert first == second


def test_rejected_beer_files_are_surfaced_with_filename_stage_and_reason():
    rejected_beer_files = [
        RejectedEnrichmentFile(filename="broken.yaml", reason_code="unparseable_yaml", reason_detail="bad YAML"),
    ]
    report = _build([], rejected_beer_files=rejected_beer_files)
    assert len(report.rejected_beer_files) == 1
    entry = report.rejected_beer_files[0]
    assert entry.filename == "broken.yaml"
    assert entry.stage == "enrichment_schema"


def test_empty_input_yields_all_zero_counts():
    report = _build([])
    assert report.total_candidates == 0
    assert report.enriched_count == 0
    assert report.remaining_count == 0
    assert report.contamination_count == 0
    assert report.structurally_blocked_count == 0
    assert report.malformed_count == 0
    assert report.rejected_beer_files == []


# ---------------------------------------------------------------------------
# Real end-to-end against the actual enrichment/ + pricing_data/ repository
# ---------------------------------------------------------------------------


def test_real_repository_dashboard():
    from tool.catalog_builder.beer_master_reader import read_beer_master_csv

    candidates_dir = Path("enrichment/candidates")
    beer_master_path = Path("pricing_data/beer_master.csv")
    if not candidates_dir.is_dir() or not beer_master_path.exists():
        import pytest

        pytest.skip("real repository data not present in this environment")

    candidates, rejected_files = validate_candidates_directory(candidates_dir)
    enrichment_report = validate_enrichment_repository(Path("enrichment"))
    terms = load_default_exclusion_terms()
    accepted, _ = read_beer_master_csv(beer_master_path)
    container_type_by_id = {row.canonical_product_id: row.container_type for row in accepted}

    report = build_enrichment_queue(
        candidates,
        rejected_files,
        enrichment_report.beers,
        terms,
        rejected_beer_files=enrichment_report.rejected_beer_files,
        container_type_by_id=container_type_by_id,
    )

    assert report.total_candidates == 1004
    assert report.contamination_count == 2
    # Real, confirmed during the founder dry run: roughly a quarter of
    # real candidates have an unmappable container_type.
    assert report.structurally_blocked_count > 200
    assert (
        report.enriched_count
        + report.remaining_count
        + report.contamination_count
        + report.structurally_blocked_count
        + report.malformed_count
        == report.total_candidates
    )
