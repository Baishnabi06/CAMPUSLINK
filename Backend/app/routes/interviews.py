import logging
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import InterviewCreate, InterviewUpdate, InterviewStatusUpdate
from app.services.google_meet import (
    create_meet_event,
    delete_meet_event,
    update_meet_event_time,
)
from app.services.notifications import create_notification, notify_all_officers
from app.services.scheduling import find_conflicts

logger = logging.getLogger(__name__)
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

    is_online = payload.mode.value == "online"

    if not is_online and not (payload.venue_or_link or "").strip():
        raise HTTPException(status_code=400, detail="Venue is required for offline interviews")

    conflicts = await find_conflicts(
        db,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        student_id=application["student_id"],
        venue_or_link=None if is_online else payload.venue_or_link,
        panel=payload.panel,
    )

    if conflicts and not payload.force:
        return {
            "success": False,
            "message": "Scheduling conflicts detected. Resolve them or resubmit with force=true to override.",
            "data": {"conflicts": conflicts},
        }

    venue_or_link = payload.venue_or_link
    calendar_event_id = None

    if is_online:
        student = await db.users.find_one({"_id": ObjectId(application["student_id"])})
        try:
            venue_or_link, calendar_event_id = await create_meet_event(
                summary=f"Interview: {student['name']} - {drive['company_name']}",
                date=payload.date,
                start_time=payload.start_time,
                end_time=payload.end_time,
                attendee_emails=[student.get("email")],
            )
        except Exception:
            logger.exception("Google Meet creation failed")
            raise HTTPException(
                status_code=502,
                detail="Could not create Google Meet link. Please try again.",
            )

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
        "venue_or_link": venue_or_link,
        "calendar_event_id": calendar_event_id,
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
        f"{payload.date} from {payload.start_time} to {payload.end_time}"
        + (f". Join: {venue_or_link}" if is_online else ""),
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
    if "mode" in fields and hasattr(fields["mode"], "value"):
        fields["mode"] = fields["mode"].value

    new_mode = fields.get("mode", interview["mode"])
    event_id = interview.get("calendar_event_id")

    if new_mode == "online":
        fields.pop("venue_or_link", None)  # the Meet link is system-managed
    elif interview["mode"] == "online" and not (fields.get("venue_or_link") or "").strip():
        raise HTTPException(
            status_code=400, detail="Venue is required when switching to offline mode"
        )

    merged = {**interview, **fields}

    conflicts = await find_conflicts(
        db,
        date=merged["date"],
        start_time=merged["start_time"],
        end_time=merged["end_time"],
        student_id=interview["student_id"],
        venue_or_link=None if new_mode == "online" else merged["venue_or_link"],
        panel=merged["panel"],
        exclude_interview_id=interview_id,
    )

    if conflicts and not payload.force:
        return {
            "success": False,
            "message": "Scheduling conflicts detected. Resolve them or resubmit with force=true to override.",
            "data": {"conflicts": conflicts},
        }

    fields["has_conflict"] = bool(conflicts)

    try:
        if new_mode == "online":
            if event_id:
                if any(k in fields for k in ("date", "start_time", "end_time")):
                    await update_meet_event_time(
                        event_id, merged["date"], merged["start_time"], merged["end_time"]
                    )
            else:  # offline -> online: create a fresh Meet
                student = await db.users.find_one({"_id": ObjectId(interview["student_id"])})
                link, new_id = await create_meet_event(
                    summary=f"Interview: {student['name']} - {interview['company_name']}",
                    date=merged["date"],
                    start_time=merged["start_time"],
                    end_time=merged["end_time"],
                    attendee_emails=[student.get("email")],
                )
                fields["venue_or_link"] = link
                fields["calendar_event_id"] = new_id
        elif event_id:  # online -> offline: withdraw the Meet
            await delete_meet_event(event_id)
            fields["calendar_event_id"] = None
    except Exception:
        logger.exception("Google Calendar sync failed")
        raise HTTPException(
            status_code=502, detail="Could not update Google Meet. Please try again."
        )

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

    update = {"status": payload.status.value}

    if payload.status.value == "cancelled" and interview.get("calendar_event_id"):
        try:
            await delete_meet_event(interview["calendar_event_id"])
            update["calendar_event_id"] = None
        except Exception:
            # Don't block cancelling if Google is unreachable or the event is already gone.
            logger.exception("Failed to delete calendar event")

    await db.interviews.update_one({"_id": oid}, {"$set": update})
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