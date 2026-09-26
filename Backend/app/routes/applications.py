from datetime import datetime, timezone
from app.services.notifications import create_notification
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import ApplicationStatusUpdate

router = APIRouter()


def check_eligibility(student: dict, drive: dict) -> tuple[bool, list[str]]:
    """Deterministic, rule-based Eligibility Filtering (NOT AI matching)."""
    reasons = []

    required_branches = drive.get("required_branches") or []
    if required_branches and student.get("branch") not in required_branches:
        reasons.append(
            f"Branch '{student.get('branch')}' is not in the required branches {required_branches}"
        )

    min_cgpa = drive.get("min_cgpa", 0)
    if (student.get("cgpa") or 0) < min_cgpa:
        reasons.append(f"CGPA {student.get('cgpa')} is below the minimum required {min_cgpa}")

    max_backlogs = drive.get("max_backlogs", 0)
    if (student.get("backlogs") or 0) > max_backlogs:
        reasons.append(f"Backlogs {student.get('backlogs')} exceed the maximum allowed {max_backlogs}")

    required_skills = drive.get("required_skills") or []
    student_skills = {s.lower() for s in (student.get("skills") or [])}
    missing_skills = [s for s in required_skills if s.lower() not in student_skills]
    if missing_skills:
        reasons.append(f"Missing required skills: {', '.join(missing_skills)}")

    required_certs = drive.get("required_certifications") or []
    student_certs = {c.lower() for c in (student.get("certifications") or [])}
    missing_certs = [c for c in required_certs if c.lower() not in student_certs]
    if missing_certs:
        reasons.append(f"Missing required certifications: {', '.join(missing_certs)}")

    return (len(reasons) == 0, reasons)


async def get_drive_or_404(db, drive_id: str):
    try:
        oid = ObjectId(drive_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid drive id")
    drive = await db.drives.find_one({"_id": oid})
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")
    return drive


def application_out(app_doc: dict) -> dict:
    app_doc = dict(app_doc)
    app_doc["id"] = str(app_doc["_id"])
    del app_doc["_id"]
    return app_doc


@router.get("/check-eligibility/{drive_id}")
async def check_drive_eligibility(
    drive_id: str, current_user: dict = Depends(require_role("student"))
):
    db = get_db()
    drive = await get_drive_or_404(db, drive_id)
    student = await db.students.find_one({"user_id": str(current_user["_id"])})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    eligible, reasons = check_eligibility(student, drive)
    return {
        "success": True,
        "message": "Eligibility checked",
        "data": {"eligible": eligible, "reasons": reasons},
    }


@router.post("/apply/{drive_id}", status_code=201)
async def apply_to_drive(drive_id: str, current_user: dict = Depends(require_role("student"))):
    db = get_db()
    drive = await get_drive_or_404(db, drive_id)

    if drive.get("status") != "open":
        raise HTTPException(status_code=400, detail="This drive is not currently open for applications")

    student_id = str(current_user["_id"])
    student = await db.students.find_one({"user_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    existing = await db.applications.find_one({"student_id": student_id, "drive_id": drive_id})
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this drive")

    eligible, reasons = check_eligibility(student, drive)
    if not eligible:
        raise HTTPException(
            status_code=400,
            detail=f"You are not eligible for this drive: {'; '.join(reasons)}",
        )

    application = {
        "student_id": student_id,
        "drive_id": drive_id,
        "status": "applied",
        "applied_at": datetime.now(timezone.utc),
        "eligibility_snapshot": {
            "branch": student.get("branch"),
            "cgpa": student.get("cgpa"),
            "backlogs": student.get("backlogs"),
            "skills": student.get("skills"),
            "certifications": student.get("certifications"),
        },
    }
    result = await db.applications.insert_one(application)
    application["_id"] = result.inserted_id

    await create_notification(
        db,
        drive["recruiter_id"],
        "New Application",
        f"{current_user['name']} applied for {drive['job_title']}",
    )

    return {"success": True, "message": "Application submitted", "data": application_out(application)}


@router.get("/mine")
async def list_my_applications(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    student_id = str(current_user["_id"])
    cursor = db.applications.find({"student_id": student_id}).sort("applied_at", -1)

    results = []
    async for app_doc in cursor:
        drive = await db.drives.find_one({"_id": ObjectId(app_doc["drive_id"])})
        out = application_out(app_doc)
        out["drive"] = (
            {
                "job_title": drive["job_title"],
                "company_name": drive["company_name"],
                "ctc": drive["ctc"],
            }
            if drive
            else None
        )
        results.append(out)

    return {"success": True, "message": "Applications fetched", "data": results}


@router.get("/drive/{drive_id}")
async def list_applicants_for_drive(
    drive_id: str, current_user: dict = Depends(require_role("recruiter"))
):
    db = get_db()
    drive = await get_drive_or_404(db, drive_id)
    if drive["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own this drive")

    cursor = db.applications.find({"drive_id": drive_id}).sort("applied_at", -1)

    results = []
    async for app_doc in cursor:
        student = await db.students.find_one({"user_id": app_doc["student_id"]})
        user_doc = await db.users.find_one({"_id": ObjectId(app_doc["student_id"])})
        out = application_out(app_doc)
        out["student"] = {
            "name": user_doc["name"] if user_doc else None,
            "email": user_doc["email"] if user_doc else None,
            "branch": student.get("branch") if student else None,
            "cgpa": student.get("cgpa") if student else None,
            "resume_url": student.get("resume_url") if student else None,
        }
        results.append(out)

    return {"success": True, "message": "Applicants fetched", "data": results}


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    current_user: dict = Depends(require_role("recruiter")),
):
    db = get_db()
    try:
        oid = ObjectId(application_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid application id")

    app_doc = await db.applications.find_one({"_id": oid})
    if not app_doc:
        raise HTTPException(status_code=404, detail="Application not found")

    drive = await db.drives.find_one({"_id": ObjectId(app_doc["drive_id"])})
    if not drive or drive["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own the drive for this application")

    await db.applications.update_one({"_id": oid}, {"$set": {"status": payload.status.value}})
    updated = await db.applications.find_one({"_id": oid})
    await create_notification(
        db,
        app_doc["student_id"],
        "Application Status Updated",
        f"Your application for {drive['job_title']} at {drive['company_name']} is now '{payload.status.value}'",
    )
    return {"success": True, "message": "Application status updated", "data": application_out(updated)}


@router.get("/all")
async def list_all_applications(current_user: dict = Depends(require_role("placement_officer"))):
    db = get_db()
    cursor = db.applications.find({}).sort("applied_at", -1)

    results = []
    async for app_doc in cursor:
        drive = await db.drives.find_one({"_id": ObjectId(app_doc["drive_id"])})
        user_doc = await db.users.find_one({"_id": ObjectId(app_doc["student_id"])})
        out = application_out(app_doc)
        out["drive_title"] = drive["job_title"] if drive else "Unknown"
        out["company_name"] = drive["company_name"] if drive else "Unknown"
        out["student_name"] = user_doc["name"] if user_doc else "Unknown"
        results.append(out)

    return {"success": True, "message": "All applications fetched", "data": results}