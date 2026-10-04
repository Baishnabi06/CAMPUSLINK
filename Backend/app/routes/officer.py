"""
Placement-officer tools: search students and view one student's full details
(profile + application / interview / offer / document tracking).

Mounted at /api/officer  (see main.py).
"""
import re
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_db
from app.core.deps import get_current_user

router = APIRouter()


def require_officer(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "placement_officer":
        raise HTTPException(status_code=403, detail="Only placement officers can use this")
    return current_user


def serialize(value):
    """Make Mongo values JSON-friendly (ObjectId -> str, datetime -> ISO string)."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)  # Mongo stores UTC
        return value.isoformat()
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(v) for v in value]
    return value


def summary_row(user: dict, student: dict | None) -> dict:
    student = student or {}
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "is_active": user.get("is_active", True),
        "branch": student.get("branch"),
        "cgpa": student.get("cgpa"),
        "backlogs": student.get("backlogs", 0),
        "profile_completed": student.get("profile_completed", False),
    }


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@router.get("/students")
async def search_students(
    q: str = Query("", max_length=80),
    limit: int = Query(20, ge=1, le=50),
    _: dict = Depends(require_officer),
):
    """Find students by name, email or branch. An empty query returns the newest students."""
    db = get_db()
    q = q.strip()
    users: dict[str, dict] = {}

    if q:
        pattern = {"$regex": re.escape(q), "$options": "i"}

        async for u in db.users.find(
            {"role": "student", "$or": [{"name": pattern}, {"email": pattern}]}
        ).limit(limit):
            users[str(u["_id"])] = u

        # students whose branch matches (branch lives in the students collection)
        branch_ids = [s["user_id"] async for s in db.students.find({"branch": pattern}).limit(limit)]
        missing = [ObjectId(i) for i in branch_ids if i not in users and ObjectId.is_valid(i)]
        if missing:
            async for u in db.users.find({"_id": {"$in": missing}, "role": "student"}):
                users[str(u["_id"])] = u
    else:
        async for u in db.users.find({"role": "student"}).sort("created_at", -1).limit(limit):
            users[str(u["_id"])] = u

    students = {
        s["user_id"]: s
        async for s in db.students.find({"user_id": {"$in": list(users.keys())}})
    }

    rows = [summary_row(u, students.get(uid)) for uid, u in users.items()]
    rows.sort(key=lambda r: r["name"].lower())

    return {
        "success": True,
        "message": f"{len(rows)} student(s) found",
        "data": rows[:limit],
    }


# ---------------------------------------------------------------------------
# One student: profile + tracking
# ---------------------------------------------------------------------------

# Field names that may link a record to a student. The first one that exists in the
# collection's documents is used, and both the user id and the student-profile id
# are accepted as values (in string and ObjectId form).
LINK_KEYS = ["student_id", "student_user_id", "user_id", "student"]


async def records_for_student(db, collection: str, ids: list, existing: set, limit: int = 50):
    """
    Returns a list of raw records, [] when there are none, or None when the
    collection is missing or we can't tell how its records link to students.
    """
    if collection not in existing:
        return None
    sample = await db[collection].find_one({})
    if sample is None:
        return []  # collection exists but is empty: genuinely nothing
    key = next((k for k in LINK_KEYS if k in sample), None)
    if key is None:
        return None
    cursor = db[collection].find({key: {"$in": ids}}).sort("_id", -1).limit(limit)
    return [doc async for doc in cursor]


@router.get("/students/{user_id}")
async def student_detail(user_id: str, _: dict = Depends(require_officer)):
    db = get_db()

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404, detail="Student not found")

    user = await db.users.find_one({"_id": ObjectId(user_id), "role": "student"})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    student = await db.students.find_one({"user_id": user_id}) or {}

    # Built field by field on purpose: never expose password_hash.
    profile = {
        "id": user_id,
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "is_active": user.get("is_active", True),
        "created_at": serialize(user.get("created_at")),
        "branch": student.get("branch"),
        "cgpa": student.get("cgpa"),
        "backlogs": student.get("backlogs", 0),
        "skills": serialize(student.get("skills", [])),
        "certifications": serialize(student.get("certifications", [])),
        "projects": serialize(student.get("projects", [])),
        "resume_url": student.get("resume_url"),
        "profile_completed": student.get("profile_completed", False),
    }

    ids = [user_id, ObjectId(user_id)]
    if student.get("_id") is not None:
        ids += [str(student["_id"]), student["_id"]]

    existing = set(await db.list_collection_names())
    applications = await records_for_student(db, "applications", ids, existing)
    interviews = await records_for_student(db, "interviews", ids, existing)
    offers = await records_for_student(db, "offers", ids, existing)
    documents = await records_for_student(db, "documents", ids, existing)

    # attach drive details (company, role...) to applications / interviews / offers
    drive_ids = set()
    for records in (applications, interviews, offers):
        for rec in records or []:
            if rec.get("drive_id"):
                drive_ids.add(str(rec["drive_id"]))

    drives: dict[str, dict] = {}
    if drive_ids and "drives" in existing:
        lookup = [ObjectId(i) for i in drive_ids if ObjectId.is_valid(i)] + list(drive_ids)
        async for d in db.drives.find({"_id": {"$in": lookup}}):
            drives[str(d["_id"])] = d

    def prepare(records, with_drive: bool):
        if records is None:
            return None
        out = []
        for rec in records:
            item = serialize(rec)
            if with_drive:
                drive = drives.get(str(rec.get("drive_id")))
                item["drive"] = serialize(drive) if drive else None
            out.append(item)
        return out

    return {
        "success": True,
        "message": "Student fetched",
        "data": {
            "profile": profile,
            "tracking": {
                "applications": prepare(applications, True),
                "interviews": prepare(interviews, True),
                "offers": prepare(offers, True),
                "documents": prepare(documents, False),
            },
        },
    }