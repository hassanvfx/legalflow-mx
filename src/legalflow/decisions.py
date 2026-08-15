"""Solo Counsel proposals and decisions with an explicit audit trail."""
from __future__ import annotations

from typing import Any

from .objects import write_object


def propose(matter, issue: str, position: str, depends_on: list[str]) -> dict[str, Any]:
    return write_object(matter, "proposal", {"issue": issue, "position": position, "depends_on": depends_on, "status": "proposed", "author": "solo_counsel"})


def accept_solo(matter, proposal_id: str, reason: str) -> dict[str, Any]:
    return write_object(matter, "decision", {"action": "accept", "object": proposal_id, "actor": "solo_counsel", "mode": "solo_counsel_auto", "reason": reason})
