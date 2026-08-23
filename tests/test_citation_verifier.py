from src.citation_verifier import (
    extract_citations,
    verify_citations,
)


def test_extract_citations():
    answer = (
        "The threshold is $2,075. "
        "Source: §6.6.1 — Amendment No. 2026-01 §3.1"
    )

    citations = extract_citations(answer)

    assert citations == ["6.6.1"]


def test_valid_citation():
    answer = (
        "The threshold is $2,075.\n\n"
        "Source: §6.6.1 — Amendment No. 2026-01 §3.1"
    )

    evidence = [
        {
            "clause_id": "6.6.1",
            "source_doc": "Amendment No. 2026-01 §3.1",
            "text": "Monthly income threshold...",
        }
    ]

    result = verify_citations(
        answer,
        evidence,
    )

    assert result["valid"] is True
    assert result["citations"] == ["6.6.1"]


def test_invalid_citation():
    answer = (
        "The threshold is $2,075.\n\n"
        "Source: §9.9.9"
    )

    evidence = [
        {
            "clause_id": "6.6.1",
            "source_doc": "Amendment No. 2026-01 §3.1",
            "text": "Monthly income threshold...",
        }
    ]

    result = verify_citations(
        answer,
        evidence,
    )

    assert result["valid"] is False
    assert "9.9.9" in result["invalid_citations"]


def test_missing_citation():
    answer = "The monthly threshold is $2,075."

    evidence = [
        {
            "clause_id": "6.6.1",
            "source_doc": "Amendment No. 2026-01 §3.1",
            "text": "Monthly income threshold...",
        }
    ]

    result = verify_citations(
        answer,
        evidence,
    )

    assert result["valid"] is False
    assert result["reason"] == (
        "No policy citation was found in the answer."
    )