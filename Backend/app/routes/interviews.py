from datetime import datetime, timezone
from app.services.notifications import create_notification, notify_all_officers
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import InterviewCreate, InterviewUpdate, InterviewStatusUpdate
from app.services.scheduling import find_conflicts

router = APIRouter()


def interview_out(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.post("", status_code=201)
async def schedule_interview(
    payload: InterviewCreate, current_user: dict = Depends(require_role("recruiter"))
):
    db = get_db()
    try:
        app_oid = ObjectId(payload.application_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid application id")

    application = await db.applications.find_one({"_id": app_oid})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    drive = await db.drives.find_one({"_id": ObjectId(application["drive_id"])})
    if not drive or drive["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own the drive for this application")

    if application["status"] not in ("shortlisted", "applied"):
        raise HTTPException(
            status_code=400,
            detail="Interviews can only be scheduled for applied or shortlisted candidates",
        )

    conflicts = await find_conflicts(
        db,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        student_id=application["student_id"],
        venue_or_link=payload.venue_or_link,
        panel=payload.panel,
    )

    if conflicts and not payload.force:
        return {
            "success": False,
            "message": "Scheduling conflicts detected. Resolve them or resubmit with force=true to override.",
            "data": {"conflicts": conflicts},
        }

    interview = {
        "student_id": application["student_id"],
        "recruiter_id": str(current_user["_id"]),
        "company_name": drive["company_name"],
        "drive_id": application["drive_id"],
        "application_id": payload.application_id,
        "date": payload.date,
        "start_time": payload.start_time,
        "end_time": payload.end_time,
        "mode": payload.mode.value,
        "venue_or_link": payload.venue_or_link,
        "panel": payload.panel,
        "status": "scheduled",
        "has_conflict": bool(conflicts),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.interviews.insert_one(interview)
    interview["_id"] = result.inserted_id
    await create_notification(
        db,
        application["student_id"],
        "Interview Scheduled",
        f"Your interview for {drive['job_title']} at {drive['company_name']} is on "
        f"{payload.date} from {payload.start_time} to {payload.end_time}",
    )

    if conflicts:
        await notify_all_officers(
            db,
            "Scheduling Conflict Detected",
            f"An interview was scheduled with conflicts on {payload.date}: {'; '.join(conflicts)}",
        )
    return {
        "success": True,
        "message": "Interview scheduled" + (" (conflicts overridden)" if conflicts else ""),
        "data": interview_out(interview),
    }


@router.get("/mine")
async def list_my_scheduled_interviews(current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    cursor = db.interviews.find({"recruiter_id": str(current_user["_id"])}).sort("date", 1)
    results = []
    async for doc in cursor:
        user_doc = await db.users.find_one({"_id": ObjectId(doc["student_id"])})
        out = interview_out(doc)
        out["student_name"] = user_doc["name"] if user_doc else "Unknown"
        results.append(out)
    return {"success": True, "message": "Interviews fetched", "data": results}


@router.get("/student/mine")
async def list_my_interviews_as_student(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    cursor = db.interviews.find({"student_id": str(current_user["_id"])}).sort("date", 1)
    results = [interview_out(doc) async for doc in cursor]
    return {"success": True, "message": "Interviews fetched", "data": results}


@router.put("/{interview_id}")
async def reschedule_interview(
    interview_id: str,
    payload: InterviewUpdate,
    current_user: dict = Depends(require_role("recruiter")),
):
    db = get_db()
    try:
        oid = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid interview id")

    interview = await db.interviews.find_one({"_id": oid})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own this interview")

    fields = {k: v for k, v in payload.model_dump().items() if v is not None and k != "force"}
    merged = {**interview, **fields}

    conflicts = await find_conflicts(
        db,
        date=merged["date"],
        start_time=merged["start_time"],
        end_time=merged["end_time"],
        student_id=interview["student_id"],
        venue_or_link=merged["venue_or_link"],
        panel=merged["panel"],
        exclude_interview_id=interview_id,
    )

    if conflicts and not payload.force:
        return {
            "success": False,
            "message": "Scheduling conflicts detected. Resolve them or resubmit with force=true to override.",
            "data": {"conflicts": conflicts},
        }

    if "mode" in fields and hasattr(fields["mode"], "value"):
        fields["mode"] = fields["mode"].value
    fields["has_conflict"] = bool(conflicts)

    await db.interviews.update_one({"_id": oid}, {"$set": fields})
    updated = await db.interviews.find_one({"_id": oid})
    return {"success": True, "message": "Interview updated", "data": interview_out(updated)}


@router.patch("/{interview_id}/status")
async def update_interview_status(
    interview_id: str,
    payload: InterviewStatusUpdate,
    current_user: dict = Depends(require_role("recruiter")),
):
    db = get_db()
    try:
        oid = ObjectId(interview_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid interview id")

    interview = await db.interviews.find_one({"_id": oid})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own this interview")

    await db.interviews.update_one({"_id": oid}, {"$set": {"status": payload.status.value}})
    updated = await db.interviews.find_one({"_id": oid})
    return {"success": True, "message": "Interview status updated", "data": interview_out(updated)}


@router.get("/all")
async def list_all_interviews(current_user: dict = Depends(require_role("placement_officer"))):
    db = get_db()
    cursor = db.interviews.find({}).sort("date", 1)
    results = []
    async for doc in cursor:
        user_doc = await db.users.find_one({"_id": ObjectId(doc["student_id"])})
        out = interview_out(doc)
        out["student_name"] = user_doc["name"] if user_doc else "Unknown"
        results.append(out)
    return {"success": True, "message": "All interviews fetched", "data": results}