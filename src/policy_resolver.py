from datetime import date
from typing import Optional


def parse_date(value: Optional[str]) -> Optional[date]:
    """Convert YYYY-MM-DD into a date object."""

    if not value:
        return None

    return date.fromisoformat(value)


def resolve_provisions(
    provisions: list[dict],
    determination_date: Optional[str] = None,
    change_date: Optional[str] = None,
):
    """
    Resolve retrieved policy provisions using the correct
    temporal trigger.

    Rules:
    - determination_date rules use the determination date.
    - change_of_circumstance_date rules use the change date.
    - If an amended clause requires a date and the date is missing,
      the system abstains instead of guessing.
    """

    determination = parse_date(determination_date)
    change = parse_date(change_date)

    resolved = []

    # Group provisions by clause.
    grouped = {}

    for provision in provisions:
        clause_id = provision["clause_id"]

        grouped.setdefault(clause_id, []).append(provision)

    for clause_id, candidates in grouped.items():

        # Find amended versions of this clause.
        amended = [
            p
            for p in candidates
            if p.get("effective_date")
        ]

        base = [
            p
            for p in candidates
            if not p.get("effective_date")
        ]

        # ---------------------------------------------------------
        # CASE 1: This clause has an amendment
        # ---------------------------------------------------------

        if amended:

            for amendment in amended:

                trigger = amendment.get("trigger")
                effective = parse_date(
                    amendment.get("effective_date")
                )

                # Determine which date controls.
                if trigger == "determination_date":
                    relevant_date = determination
                    required_date = "determination_date"

                elif trigger == "change_of_circumstance_date":
                    relevant_date = change
                    required_date = "change_date"

                else:
                    relevant_date = None
                    required_date = None

                status_map = {}

                # -------------------------------------------------
                # Date is required but missing
                # -------------------------------------------------

                if required_date and relevant_date is None:

                    for p in candidates:
                        status_map[id(p)] = {
                            "applicable": False,
                            "needs_date": required_date,
                            "resolution_reason": (
                                f"{required_date} is required to "
                                f"resolve amended clause §{clause_id}."
                            ),
                        }

                # -------------------------------------------------
                # Date available
                # -------------------------------------------------

                elif relevant_date is not None and effective is not None:

                    if relevant_date >= effective:

                        # Amendment wins.
                        for p in candidates:
                            if p in amended:
                                status_map[id(p)] = {
                                    "applicable": True,
                                    "needs_date": None,
                                    "resolution_reason": (
                                        f"§{clause_id} was amended effective "
                                        f"{effective.isoformat()} and the "
                                        f"relevant date is "
                                        f"{relevant_date.isoformat()}."
                                    ),
                                }
                            else:
                                status_map[id(p)] = {
                                    "applicable": False,
                                    "needs_date": None,
                                    "resolution_reason": (
                                        f"Superseded by Amendment No. "
                                        f"2026-01 effective "
                                        f"{effective.isoformat()}."
                                    ),
                                }

                    else:

                        # Base wins.
                        for p in candidates:
                            if p in base:
                                status_map[id(p)] = {
                                    "applicable": True,
                                    "needs_date": None,
                                    "resolution_reason": (
                                        f"Relevant date "
                                        f"{relevant_date.isoformat()} "
                                        f"is before amendment effective "
                                        f"date {effective.isoformat()}."
                                    ),
                                }
                            else:
                                status_map[id(p)] = {
                                    "applicable": False,
                                    "needs_date": None,
                                    "resolution_reason": (
                                        f"Amendment becomes effective "
                                        f"{effective.isoformat()}, after the "
                                        f"relevant date."
                                    ),
                                }

                for p in candidates:
                    info = status_map.get(
                        id(p),
                        {
                            "applicable": True,
                            "needs_date": None,
                            "resolution_reason": "No superseding amendment was found.",
                        },
                    )
                    resolved.append({**p, **info})

            continue

        # ---------------------------------------------------------
        # CASE 2: No amendment for this clause
        # ---------------------------------------------------------

        for provision in candidates:

            resolved.append({
                **provision,
                "applicable": True,
                "needs_date": None,
                "resolution_reason": (
                    "No superseding amendment was found."
                ),
            })

    return resolved


def get_applicable_provisions(resolved):
    """Return only provisions that are applicable."""

    return [
        provision
        for provision in resolved
        if provision.get("applicable") is True
    ]


def get_required_date(resolved):
    """Return the date required to resolve the policy."""

    for provision in resolved:

        if provision.get("needs_date"):
            return provision["needs_date"]

    return None