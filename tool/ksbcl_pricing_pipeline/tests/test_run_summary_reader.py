import json

from tool.ksbcl_pricing_pipeline.run_summary_reader import read_source_pdf_reference


def test_reads_source_pdf_reference(tmp_path):
    path = tmp_path / "run_summary.json"
    path.write_text(json.dumps({"source_pdf_reference": "pricing_data/raw_pdfs/2026-06/x.pdf", "other": 1}))

    assert read_source_pdf_reference(path) == "pricing_data/raw_pdfs/2026-06/x.pdf"
