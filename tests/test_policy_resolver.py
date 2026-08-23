from src.policy_resolver import resolve_provisions


def test_determination_date_after_amendment():
    provisions = [
        {
            "clause_id": "6.6.1",
            "text": "Old threshold",
            "source_doc": "Policy Manual",
            "trigger": None,
            "effective_date": None,
        },
        {
            "clause_id": "6.6.1",
            "text": "New threshold",
            "source_doc": "Amendment No. 2026-01",
            "trigger": "determination_date",
            "effective_date": "2026-03-01",
        },
    ]

    result = resolve_provisions(
        provisions,
        determination_date="2026-04-15",
    )

    assert result[1]["applicable"] is True
    assert result[1]["text"] == "New threshold"


def test_determination_date_before_amendment():
    provisions = [
        {
            "clause_id": "6.6.1",
            "text": "Old threshold",
            "source_doc": "Policy Manual",
            "trigger": None,
            "effective_date": None,
        },
        {
            "clause_id": "6.6.1",
            "text": "New threshold",
            "source_doc": "Amendment No. 2026-01",
            "trigger": "determination_date",
            "effective_date": "2026-03-01",
        },
    ]

    result = resolve_provisions(
        provisions,
        determination_date="2026-02-15",
    )

    assert result[1]["applicable"] is False


def test_change_date_after_amendment():
    provisions = [
        {
            "clause_id": "4.3.2",
            "text": "14 calendar days",
            "source_doc": "Amendment No. 2026-01",
            "trigger": "change_of_circumstance_date",
            "effective_date": "2026-03-01",
        }
    ]

    result = resolve_provisions(
        provisions,
        change_date="2026-03-01",
    )

    assert result[0]["applicable"] is True


def test_change_date_before_amendment():
    provisions = [
        {
            "clause_id": "4.3.2",
            "text": "14 calendar days",
            "source_doc": "Amendment No. 2026-01",
            "trigger": "change_of_circumstance_date",
            "effective_date": "2026-03-01",
        }
    ]

    result = resolve_provisions(
        provisions,
        change_date="2026-02-28",
    )

    assert result[0]["applicable"] is False


def test_missing_change_date():
    provisions = [
        {
            "clause_id": "4.3.2",
            "text": "14 calendar days",
            "source_doc": "Amendment No. 2026-01",
            "trigger": "change_of_circumstance_date",
            "effective_date": "2026-03-01",
        }
    ]

    result = resolve_provisions(provisions)

    assert result[0]["applicable"] is False
    assert result[0]["needs_date"] == "change_date"