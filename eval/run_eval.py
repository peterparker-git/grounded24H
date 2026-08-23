import json
import sys
import time
from pathlib import Path

# Allow imports from src/
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

# pyrefly: ignore [missing-import]
from policy_engine import resolve_policy

# pyrefly: ignore [missing-import]
from confidence import is_relevant

TEST_FILE = Path(__file__).parent / "test_cases.json"


def load_cases():
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_clause_ids(response):
    """
    Extract clause IDs from the verified source list.
    """

    sources = response.get("source") or []

    return {
        str(source["clause_id"])
        for source in sources
    }


def run():
    cases = load_cases()

    passed = 0
    failed = 0

    print()
    print("=" * 80)
    print("GROUNDED POLICY EVALUATION")
    print("=" * 80)

    for case in cases:

        result = resolve_policy(
            question=case["question"],
            determination_date=case.get(
                "determination_date"
            ),
            change_date=case.get(
                "change_date"
            ),
        )

        policy_status = result["status"]
        top_score = result.get("top_score", 0.0)

        # -------------------------------------------------
        # Apply the same relevance rule used by assistant.py
        # -------------------------------------------------

        if policy_status == "RESOLVED":

            if is_relevant(top_score):
                actual_status = "ANSWERED"
            else:
                actual_status = "ABSTAIN"

        elif policy_status == "NEEDS_DATE":

            if is_relevant(top_score):
                actual_status = "NEEDS_DATE"
            else:
                actual_status = "ABSTAIN"

        elif policy_status in {
            "NOT_FOUND",
            "NO_APPLICABLE_POLICY",
        }:

            actual_status = "ABSTAIN"

        else:
            actual_status = policy_status

        expected_status = case["expected_status"]

        # -------------------------------------------------
        # Status verification
        # -------------------------------------------------

        status_ok = (
            actual_status == expected_status
        )

        # -------------------------------------------------
        # Clause verification
        # -------------------------------------------------

        clause_ok = True

        expected_clause = case.get(
            "expected_clause"
        )

        if expected_clause:

            applicable = result.get(
                "applicable",
                []
            )

            actual_clauses = {
                str(item["clause_id"])
                for item in applicable
            }

            clause_ok = (
                expected_clause
                in actual_clauses
            )

        # -------------------------------------------------
        # Final result
        # -------------------------------------------------

        test_passed = (
            status_ok
            and clause_ok
        )

        if test_passed:
            passed += 1
            marker = "PASS"
        else:
            failed += 1
            marker = "FAIL"

        print()
        print(
            f"[{marker}] {case['id']}"
        )

        print(
            f"  Expected: {expected_status}"
        )

        print(
            f"  Actual:   {actual_status}"
        )

        if expected_clause:

            print(
                f"  Expected clause: "
                f"§{expected_clause}"
            )

            print(
                f"  Actual clauses: "
                f"{sorted(actual_clauses)}"
            )

        print(
            f"  Score: "
            f"{result.get('top_score', 0.0):.4f}"
        )

    print()
    print("=" * 80)

    print(
        f"Passed: {passed}/{len(cases)}"
    )

    print(
        f"Failed: {failed}/{len(cases)}"
    )

    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run())