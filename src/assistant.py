from policy_engine import resolve_policy
from generator import generate_answer


def run_assistant(
    question: str,
    determination_date: str | None = None,
    change_date: str | None = None,
):
    """
    Main Grounded Answer assistant pipeline.

    Flow:
        Question
          ↓
        Policy Engine
          ↓
        NEEDS_DATE / RESOLVED / NOT_FOUND
          ↓
        Gemini grounded generation
    """

    # ---------------------------------------------------------
    # 1. Resolve policy
    # ---------------------------------------------------------

    result = resolve_policy(
        question=question,
        determination_date=determination_date,
        change_date=change_date,
    )

    # ---------------------------------------------------------
    # 2. Policy requires additional date information
    # ---------------------------------------------------------

    if result["status"] == "NEEDS_DATE":

        required_date = result["needs_date"]

        if required_date == "determination_date":
            message = (
                "I need the determination date to answer "
                "this question because the applicable policy "
                "depends on when the determination was made."
            )

        elif required_date == "change_of_circumstance_date":
            message = (
                "I need the date when the change of "
                "circumstances occurred because the applicable "
                "reporting rule depends on that date."
            )

        else:
            message = (
                "I need additional date information to "
                "determine which policy rule applies."
            )

        return {
            "status": "NEEDS_DATE",
            "answer": message,
            "source": None,
            "policy": result,
        }

    # ---------------------------------------------------------
    # 3. No policy found
    # ---------------------------------------------------------

    if result["status"] in {
        "NOT_FOUND",
        "NO_APPLICABLE_POLICY",
    }:

        message = (
            "I don't know based on the policy manual.\n\n"
            "Please ask the Program Supervisor."
        )

        return {
            "status": "ABSTAIN",
            "answer": message,
            "source": None,
            "policy": result,
        }

    # ---------------------------------------------------------
    # 4. Policy successfully resolved
    # ---------------------------------------------------------

    applicable_policy = result["applicable"]

    answer = generate_answer(
        question=question,
        policy_evidence=applicable_policy,
    )

    # ---------------------------------------------------------
    # 5. Return final answer
    # ---------------------------------------------------------

    source = []

    for item in applicable_policy:

        source.append({
            "clause_id": item["clause_id"],
            "source_doc": item["source_doc"],
        })

    return {
        "status": "ANSWERED",
        "answer": answer,
        "source": source,
        "policy": result,
    }


def print_response(response):
    """
    Display the assistant response.
    """

    print()
    print("=" * 70)
    print("GROUNDED ANSWER ASSISTANT")
    print("=" * 70)

    print()
    print(response["answer"])

    if response["source"]:

        print()
        print("Verified policy source:")

        for source in response["source"]:

            print(
                f"§{source['clause_id']} "
                f"— {source['source_doc']}"
            )

    print()
    print("=" * 70)


if __name__ == "__main__":

    print()
    print("=" * 70)
    print("GROUNDED ANSWER ASSISTANT")
    print("=" * 70)

    print()
    print("Type 'exit' to quit.")
    print()

    while True:

        question = input("Question: ").strip()

        if question.lower() == "exit":
            print("Goodbye.")
            break

        if not question:
            print("Please enter a question.")
            continue

        determination_date = input(
            "Determination date "
            "(YYYY-MM-DD, optional): "
        ).strip() or None

        change_date = input(
            "Change-of-circumstance date "
            "(YYYY-MM-DD, optional): "
        ).strip() or None

        response = run_assistant(
            question=question,
            determination_date=determination_date,
            change_date=change_date,
        )

        print_response(response)