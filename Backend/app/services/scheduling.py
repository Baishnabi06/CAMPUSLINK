"""
Modular interview scheduling + conflict detection.

Kept separate from the route layer on purpose: this is the piece most
likely to grow into something smarter later (auto-scheduling, panel
load-balancing, etc.) and route handlers shouldn't need to change when it does.
"""

from bson import ObjectId


def _to_minutes(hhmm: str) -> int:
    hours, minutes = map(int, hhmm.split(":"))
    return hours * 60 + minutes


def _ranges_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    return _to_minutes(start1) < _to_minutes(end2) and _to_minutes(start2) < _to_minutes(end1)


async def find_conflicts(
    db,
    date: str,
    start_time: str,
    end_time: str,
    student_id: str,
    venue_or_link: str,
    panel: list[str],
    exclude_interview_id: str | None = None,
) -> list[str]:
    """Returns a list of human-readable conflict descriptions (empty = no conflicts)."""
    conflicts = []

    query = {"date": date, "status": "scheduled"}
    if exclude_interview_id:
        query["_id"] = {"$ne": ObjectId(exclude_interview_id)}

    cursor = db.interviews.find(query)
    async for existing in cursor:
        if not _ranges_overlap(start_time, end_time, existing["start_time"], existing["end_time"]):
            continue

        if existing["student_id"] == student_id:
            conflicts.append(
                f"Student already has an overlapping interview on {date} "
                f"({existing['start_time']}-{existing['end_time']})"
            )

        if existing["venue_or_link"] == venue_or_link:
            conflicts.append(
                f"Venue/link '{venue_or_link}' is already booked on {date} "
                f"({existing['start_time']}-{existing['end_time']})"
            )

        shared_panel = {p.lower() for p in existing.get("panel", [])} & {p.lower() for p in panel}
        if shared_panel:
            conflicts.append(
                f"Panel member(s) {', '.join(shared_panel)} already assigned on {date} "
                f"({existing['start_time']}-{existing['end_time']})"
            )

    return conflicts