import re

def generate_fallback_answer(question: str, policy_evidence: list[dict]) -> str:
    """
    Generates a deterministic plain-language answer without using an LLM.
    Relies purely on regular expressions to extract known facts from the 
    provided policy evidence.
    """
    if not policy_evidence:
        return (
            "I don't know based on the policy manual.\n\n"
            "Please ask the Program Supervisor."
        )

    q_lower = question.lower()

    # 1. Income threshold
    if "income threshold" in q_lower and "household of" in q_lower:
        match = re.search(r"household of (\d+)", q_lower)
        if match:
            size = match.group(1)
            for item in policy_evidence:
                text = item.get("text", "")
                # Example: "household size 1: $1,225; 2: $1,650; 3: $2,075;"
                # Example historical: "1: $1,180; 2: $1,590; 3: $2,000;"
                size_match = re.search(rf"\b{size}:\s*\$([0-9,]+)", text)
                if size_match:
                    amount = size_match.group(1)
                    return f"The monthly income threshold for a household of {size} is ${amount}."

    # 2. Reporting changes
    if "report a change" in q_lower or "reporting" in q_lower or "change of circumstances" in q_lower:
        for item in policy_evidence:
            text = item.get("text", "")
            # Look for something like "14 calendar days" or "10 calendar days"
            days_match = re.search(r"(\d+)\s+calendar days", text, re.IGNORECASE)
            if days_match:
                days = days_match.group(1)
                return f"A recipient must report a change of circumstances within {days} calendar days."

    # 3. Default safe fallback
    return (
        "The applicable policy provision was found, but a plain-language "
        "answer could not be generated because the AI service is currently "
        "unavailable."
    )
