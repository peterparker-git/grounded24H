from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Provision:
    clause_id: str
    text: str
    source_doc: str

    supersedes: Optional[str] = None

    trigger: Optional[str] = None
    effective_date: Optional[str] = None

    retroactive: bool = False
    apportionable: bool = False

    superseded_value: Optional[str] = None

    def to_dict(self):
        return asdict(self)