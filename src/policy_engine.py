from retriever import retrieve
from policy_resolver import (
    resolve_provisions,
    get_required_date,
)

def filter_relevant_candidates(
    candidates: list[dict],
    score_margin: float = 0.03,
    max_results: int = 3,
) -> list[dict]:
    """
    Keep strongly relevant candidates while preserving the
    base/amendment versions of the same clause.

    Example:

        §4.3.2 Amendment  -> keep
        §4.3.2 Base       -> keep

    But unrelated clauses such as §9.1.4 are filtered out
    when they fall outside the relevance margin.
    """

    if not candidates:
        return []

    top_score = candidates[0]["score"]
    threshold = top_score - score_margin

    relevant = []

    # ---------------------------------------------------------
    # 1. Keep candidates close to the strongest match
    # ---------------------------------------------------------

    for candidate in candidates:

        if candidate["score"] >= threshold:
            relevant.append(candidate)

    # ---------------------------------------------------------
    # 2. Preserve the base/amendment pair of the strongest
    #    clause.
    # ---------------------------------------------------------

    top_clause_id = candidates[0]["clause_id"]

    for candidate in candidates:

        if candidate["clause_id"] == top_clause_id:

            if candidate not in relevant:
                relevant.append(candidate)

    # ---------------------------------------------------------
    # 3. Keep the strongest results first.
    # ---------------------------------------------------------

    relevant.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return relevant[:max_results]
    
def resolve_policy(
    question: str,
    determination_date: str | None = None,
    change_date: str | None = None,
    top_k: int = 5,
):
    """
    Retrieve relevant policy provisions and resolve
    which provisions are applicable for the supplied dates.

    The engine will NOT fall back to an unrelated policy clause
    when the strongest matching amended provision requires a
    missing date.
    """

    # ---------------------------------------------------------
    # 1. Retrieve relevant policy provisions
    # ---------------------------------------------------------

    retrieved_candidates = retrieve(
        question,
        top_k=top_k,
    )

    candidates = filter_relevant_candidates(
        retrieved_candidates
    )

    # ---------------------------------------------------------
    # 2. No policy candidates found
    # ---------------------------------------------------------

    if not candidates:
        return {
            "status": "NOT_FOUND",
            "question": question,
            "candidates": [],
            "resolved": [],
            "applicable": [],
            "needs_date": None,
        }

    # ---------------------------------------------------------
    # 3. Check the strongest retrieved candidate
    #    for a required temporal date.
    #
    #    This prevents the engine from falling back to an
    #    unrelated lower-ranked clause.
    # ---------------------------------------------------------

    top_candidate = candidates[0]

    trigger = top_candidate.get("trigger")
    effective_date = top_candidate.get("effective_date")

    missing_required_date = (
        trigger == "determination_date"
        and not determination_date
    ) or (
        trigger == "change_of_circumstance_date"
        and not change_date
    )

    if effective_date and missing_required_date:
        return {
            "status": "NEEDS_DATE",
            "question": question,
            "candidates": candidates,
            "resolved": [],
            "applicable": [],
            "needs_date": trigger,
        }

    # ---------------------------------------------------------
    # 4. Resolve provisions using temporal rules
    # ---------------------------------------------------------

    resolved = resolve_provisions(
        candidates,
        determination_date=determination_date,
        change_date=change_date,
    )

    # ---------------------------------------------------------
    # 5. Get provisions that are actually applicable
    # ---------------------------------------------------------

    applicable = [
        item
        for item in resolved
        if item.get("applicable") is True
    ]

    # ---------------------------------------------------------
    # 6. Check whether the resolver still needs a date
    # ---------------------------------------------------------

    required_date = get_required_date(resolved)

    if required_date:
        return {
            "status": "NEEDS_DATE",
            "question": question,
            "candidates": candidates,
            "resolved": resolved,
            "applicable": [],
            "needs_date": required_date,
        }

    # ---------------------------------------------------------
    # 7. No applicable policy
    # ---------------------------------------------------------

    if not applicable:
        return {
            "status": "NO_APPLICABLE_POLICY",
            "question": question,
            "candidates": candidates,
            "resolved": resolved,
            "applicable": [],
            "needs_date": None,
        }

    # ---------------------------------------------------------
    # 8. Successfully resolved
    # ---------------------------------------------------------

    return {
        "status": "RESOLVED",
        "question": question,
        "candidates": candidates,
        "resolved": resolved,
        "applicable": applicable,
        "needs_date": None,
    }


def print_policy_result(result):
    """
    Print the policy engine result in a readable format.
    """

    print()
    print("=" * 70)
    print("POLICY ENGINE")
    print("=" * 70)

    print()
    print("Question:")
    print(result["question"])

    print()
    print(f"Status: {result['status']}")

    # ---------------------------------------------------------
    # Missing date
    # ---------------------------------------------------------

    if result["status"] == "NEEDS_DATE":

        print()
        print("Missing information:")
        print(result["needs_date"])

    # ---------------------------------------------------------
    # Resolved policy
    # ---------------------------------------------------------

    if result["status"] == "RESOLVED":

        print()
        print("Applicable policy:")

        for item in result["applicable"]:

            print()
            print(f"§{item['clause_id']}")
            print(f"Source: {item['source_doc']}")
            print(f"Text: {item['text']}")

            print(
                "Reason: "
                f"{item.get('resolution_reason', '')}"
            )

    # ---------------------------------------------------------
    # No applicable policy
    # ---------------------------------------------------------

    if result["status"] == "NO_APPLICABLE_POLICY":

        print()
        print(
            "No applicable policy provision "
            "was found."
        )

    # ---------------------------------------------------------
    # No results
    # ---------------------------------------------------------

    if result["status"] == "NOT_FOUND":

        print()
        print(
            "No relevant policy provision "
            "was found."
        )

    print()
    print("=" * 70)


if __name__ == "__main__":

    question = input(
        "Policy question: "
    ).strip()

    determination_date = input(
        "Determination date (YYYY-MM-DD, optional): "
    ).strip() or None

    change_date = input(
        "Change-of-circumstance date "
        "(YYYY-MM-DD, optional): "
    ).strip() or None

    result = resolve_policy(
        question=question,
        determination_date=determination_date,
        change_date=change_date,
    )

    print_policy_result(result)