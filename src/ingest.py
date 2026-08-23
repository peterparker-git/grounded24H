import json
import re
from pathlib import Path

from models import Provision


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

BASE_MANUAL = DATA_DIR / "manual_base.md"
AMENDMENT = DATA_DIR / "amendments" / "2026-01.md"
OUTPUT_FILE = DATA_DIR / "provisions.jsonl"


CLAUSE_PATTERN = re.compile(
    r"^\*\*(\d+(?:\.\d+)+(?:\([a-z]\))?)\*\*\s+(.*)$"
)


def parse_base_manual():
    """
    Extract numbered provisions from the consolidated
    policy manual.
    """

    provisions = []

    lines = BASE_MANUAL.read_text(encoding="utf-8").splitlines()

    current_clause = None
    current_text = []

    def save_current():
        nonlocal current_clause, current_text

        if current_clause and current_text:
            text = " ".join(
                line.strip()
                for line in current_text
                if line.strip()
            )

            provisions.append(
                Provision(
                    clause_id=current_clause,
                    text=text,
                    source_doc="Policy Manual",
                )
            )

        current_clause = None
        current_text = []

    for line in lines:
        match = CLAUSE_PATTERN.match(line.strip())

        if match:
            save_current()

            current_clause = match.group(1)
            current_text = [match.group(2)]

        elif current_clause:
            stripped = line.strip()

            if stripped:
                current_text.append(stripped)

    save_current()

    return provisions


def add_amendment_provisions(provisions):
    """
    Add structured provisions introduced or modified
    by Amendment No. 2026-01.
    """

    provisions.extend(
        [
            Provision(
                clause_id="6.4.1(a)",
                text="The earnings disregard is $175 per month.",
                source_doc="Amendment No. 2026-01 §1.1",
                supersedes="6.4.1(a)",
                trigger="determination_date",
                effective_date="2026-03-01",
                retroactive=True,
                apportionable=False,
                superseded_value="$120 per month",
            ),

            Provision(
                clause_id="4.3.2",
                text=(
                    "A recipient must report a change of circumstances "
                    "within 14 calendar days."
                ),
                source_doc="Amendment No. 2026-01 §2.1",
                supersedes="4.3.2",
                trigger="change_of_circumstance_date",
                effective_date="2026-03-01",
                retroactive=False,
                apportionable=False,
                superseded_value="10 calendar days",
            ),

            Provision(
                clause_id="9.1.4",
                text=(
                    "Where an overpayment has arisen from a change of "
                    "circumstances, the applicable reporting period is "
                    "14 calendar days."
                ),
                source_doc="Amendment No. 2026-01 §2.2",
                supersedes="9.1.4",
                trigger="change_of_circumstance_date",
                effective_date="2026-03-01",
                retroactive=False,
                apportionable=False,
                superseded_value="30 calendar days",
            ),

            Provision(
                clause_id="6.6.1",
                text=(
                    "Monthly income thresholds are: "
                    "household size 1: $1,225; "
                    "2: $1,650; "
                    "3: $2,075; "
                    "4: $2,500; "
                    "5: $2,925; "
                    "each additional member: +$425."
                ),
                source_doc="Amendment No. 2026-01 §3.1",
                supersedes="6.6.1",
                trigger="determination_date",
                effective_date="2026-03-01",
                retroactive=True,
                apportionable=True,
                superseded_value=(
                    "1: $1,180; 2: $1,590; 3: $2,000; "
                    "4: $2,410; 5: $2,820; "
                    "each additional member: +$410"
                ),
            ),

            Provision(
                clause_id="10.5.2",
                text="The sanction is a 15 per cent reduction.",
                source_doc="Amendment No. 2026-01 §4.1",
                supersedes="10.5.2",
                trigger="determination_date",
                effective_date="2026-03-01",
                retroactive=True,
                apportionable=False,
                superseded_value="20 per cent",
            ),

            Provision(
                clause_id="10.5.3A",
                text=(
                    "A sanction must not be imposed in respect of a "
                    "failure to report where the change of circumstances "
                    "would have increased the award."
                ),
                source_doc="Amendment No. 2026-01 §4.2",
                supersedes=None,
                trigger="determination_date",
                effective_date="2026-03-01",
                retroactive=True,
                apportionable=False,
            ),
        ]
    )

    return provisions


def save_provisions(provisions):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for provision in provisions:
            file.write(
                json.dumps(
                    provision.to_dict(),
                    ensure_ascii=False
                )
                + "\n"
            )


def main():
    print("Reading base policy manual...")

    provisions = parse_base_manual()

    print(f"Extracted {len(provisions)} base provisions.")

    print("Adding Amendment No. 2026-01...")

    provisions = add_amendment_provisions(provisions)

    print(f"Total provisions: {len(provisions)}")

    save_provisions(provisions)

    print(f"Saved provisions to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()