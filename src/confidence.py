MIN_RELEVANCE_SCORE = 0.70


def is_relevant(score: float) -> bool:
    """
    Determine whether a retrieved result is sufficiently
    relevant to continue answering.
    """

    return score >= MIN_RELEVANCE_SCORE


def check_confidence(policy_result: dict) -> bool:
    """
    Check whether the policy engine has sufficient
    retrieval confidence.
    """

    if policy_result["status"] != "RESOLVED":
        return False

    score = policy_result.get("top_score", 0.0)

    return is_relevant(score)
