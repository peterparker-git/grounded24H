import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.6-flash"


SYSTEM_INSTRUCTION = """
You are the Grounded Answer assistant for a county benefits office.

Your job is to explain policy information in plain language.

STRICT RULES:

1. Use ONLY the policy evidence provided to you.
2. Never invent policy facts.
3. Never infer a value that is not explicitly supported by the evidence.
4. Do not change, reinterpret, or override the policy.
5. The application has already determined which policy provision applies.
6. Always cite the exact policy clause used.
7. Keep the answer concise and easy to understand.
8. If the evidence does not support an answer, say:
   "I don't know based on the policy manual."
9. When the evidence is insufficient, do not guess.
10. Do not cite a clause that is not present in the supplied evidence.

Answer format:

Answer:
<plain-language answer>

Source:
§<clause number> — <source document>

If the evidence is insufficient:

Answer:
I don't know based on the policy manual.

Please ask the Program Supervisor.
"""


import time

def generate_answer(
    question: str,
    policy_evidence: list[dict],
    max_retries: int = 5,
    initial_delay: float = 22.0,
) -> str:
    """
    Generate a plain-language answer using ONLY
    the policy evidence resolved by the policy engine.
    Includes exponential backoff for 429 rate limits.
    """

    if not policy_evidence:
        return (
            "I don't know based on the policy manual.\n\n"
            "Please ask the Program Supervisor."
        )

    evidence_text = []

    for item in policy_evidence:

        evidence_text.append(
            f"""
CLAUSE: §{item["clause_id"]}
SOURCE: {item["source_doc"]}
TEXT: {item["text"]}
"""
        )

    evidence = "\n".join(evidence_text)

    prompt = f"""
{SYSTEM_INSTRUCTION}

USER QUESTION:
{question}

RESOLVED POLICY EVIDENCE:
{evidence}

Now answer the user's question using ONLY the resolved policy evidence.
"""

    delay = initial_delay
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            # IMMEDIATE FALLBACK for quota limits
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower() or "rate limit" in str(e).lower():
                raise
            
            if attempt < max_retries - 1:
                print(f"\nTransient error. Waiting {delay:.1f}s before retrying (attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
                delay *= 1.5
                continue
            raise


if __name__ == "__main__":

    question = input(
        "Question: "
    ).strip()

    example_policy = [
        {
            "clause_id": "6.6.1",
            "source_doc": "Amendment No. 2026-01 §3.1",
            "text": (
                "Monthly income thresholds are: "
                "household size 1: $1,225; "
                "2: $1,650; "
                "3: $2,075; "
                "4: $2,500; "
                "5: $2,925; "
                "each additional member: +$425."
            ),
        }
    ]

    answer = generate_answer(
        question,
        example_policy,
    )

    print()
    print("=" * 70)
    print("GROUNDED ANSWER")
    print("=" * 70)
    print()
    print(answer)