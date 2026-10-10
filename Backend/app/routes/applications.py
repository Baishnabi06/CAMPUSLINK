from datetime import datetime, timezone

from app.services.notifications import create_notification
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import (
    ApplicationStatusUpdate,
    RoundStatusUpdate,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

def check_eligibility(student: dict, drive: dict) -> tuple[bool, list[str]]:
    """Deterministic, rule-based Eligibility Filtering (NOT AI matching)."""
    reasons = []

    required_branches = drive.get("required_branches") or []
    if required_branches and student.get("branch") not in required_branches:
        reasons.append(
            f"Branch '{student.get('branch')}' is not in the required branches "
            f"{required_branches}"
        )

    min_cgpa = drive.get("min_cgpa", 0)
    if (student.get("cgpa") or 0) < min_cgpa:
        reasons.append(
            f"CGPA {student.get('cgpa')} is below the minimum required {min_cgpa}"
        )

    max_backlogs = drive.get("max_backlogs", 0)
    if (student.get("backlogs") or 0) > max_backlogs:
        reasons.append(
            f"Backlogs {student.get('backlogs')} exceed the maximum allowed "
            f"{max_backlogs}"
        )

    required_skills = drive.get("required_skills") or []
    student_skills = {
        s.lower() for s in (student.get("skills") or [])
    }

    missing_skills = [
        s for s in required_skills
        if s.lower() not in student_skills
    ]

    if missing_skills:
        reasons.append(
            f"Missing required skills: {', '.join(missing_skills)}"
        )

    required_certs = drive.get("required_certifications") or []
    student_certs = {
        c.lower() for c in (student.get("certifications") or [])
    }

    missing_certs = [
        c for c in required_certs
        if c.lower() not in student_certs
    ]

    if missing_certs:
        reasons.append(
            f"Missing required certifications: {', '.join(missing_certs)}"
        )

    return (len(reasons) == 0, reasons)


# ---------------------------------------------------------------------------
# Drive helper
# ---------------------------------------------------------------------------

async def get_drive_or_404(db, drive_id: str):
    try:
        oid = ObjectId(drive_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid drive id"
        )

    drive = await db.drives.find_one({"_id": oid})

    if not drive:
        raise HTTPException(
            status_code=404,
            detail="Drive not found"
        )

    return drive


# ---------------------------------------------------------------------------
# Placement Round Helpers
# ---------------------------------------------------------------------------

DEFAULT_ROUNDS = [
    "Technical Interview",
    "HR Interview",
]


def build_application_rounds(drive: dict) -> list[dict]:
    """
    Creates the round pipeline for a new application.

    Recruiter-selected rounds are read from:
        drive["selection_rounds"]

    Example:
        [
            "Technical Interview",
            "HR Interview"
        ]

    If the field does not exist yet, CampusLink uses the default:
        Technical Interview -> HR Interview
    """

    selected_rounds = drive.get("selection_rounds")

    if not selected_rounds:
        selected_rounds = DEFAULT_ROUNDS

    rounds = []

    for index, round_name in enumerate(selected_rounds):
        rounds.append(
            {
                "round_number": index + 1,
                "name": round_name,
                "status": "pending" if index == 0 else "locked",
                "score": None,
                "updated_at": None,
                "feedback": None,
            }
        )

    return rounds


def get_current_round_index(rounds: list[dict]) -> int | None:
    """
    Returns the index of the first pending round.
    """

    for index, round_data in enumerate(rounds):
        if round_data.get("status") == "pending":
            return index

    return None


def update_round_pipeline(
    rounds: list[dict],
    round_index: int,
    status: str,
    score: float,
    feedback: str | None = None,
) -> list[dict]:

    if round_index < 0 or round_index >= len(rounds):
        raise HTTPException(
            status_code=400,
            detail="Invalid round number"
        )

    current_round = rounds[round_index]

    # ---------------------------------------------------------
    # Only the currently unlocked/pending round can be updated.
    # ---------------------------------------------------------

    if current_round.get("status") != "pending":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Round '{current_round.get('name')}' is not currently "
                f"available for evaluation"
            ),
        )

    # ---------------------------------------------------------
    # Score validation
    # ---------------------------------------------------------

    if score < 0 or score > 100:
        raise HTTPException(
            status_code=400,
            detail="Score must be between 0 and 100"
        )

    current_round["status"] = status
    current_round["score"] = score
    current_round["updated_at"] = datetime.now(timezone.utc)
    current_round["feedback"] = feedback

    # ---------------------------------------------------------
    # If passed:
    # Unlock next round automatically.
    # ---------------------------------------------------------

    if status == "passed":
        next_index = round_index + 1

        if next_index < len(rounds):
            rounds[next_index]["status"] = "pending"

    # ---------------------------------------------------------
    # If failed:
    # Keep remaining rounds locked.
    # ---------------------------------------------------------

    elif status == "failed":
        for index in range(round_index + 1, len(rounds)):
            rounds[index]["status"] = "locked"

    return rounds


# ---------------------------------------------------------------------------
# Application output
# ---------------------------------------------------------------------------

def application_out(app_doc: dict) -> dict:
    app_doc = dict(app_doc)

    app_doc["id"] = str(app_doc["_id"])

    del app_doc["_id"]

    return app_doc


# ---------------------------------------------------------------------------
# Check eligibility
# ---------------------------------------------------------------------------

@router.get("/check-eligibility/{drive_id}")
async def check_drive_eligibility(
    drive_id: str,
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()

    drive = await get_drive_or_404(db, drive_id)

    student = await db.students.find_one(
        {"user_id": str(current_user["_id"])}
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    eligible, reasons = check_eligibility(student, drive)

    return {
        "success": True,
        "message": "Eligibility checked",
        "data": {
            "eligible": eligible,
            "reasons": reasons,
        },
    }


# ---------------------------------------------------------------------------
# Apply to drive
# ---------------------------------------------------------------------------

@router.post("/apply/{drive_id}", status_code=201)
async def apply_to_drive(
    drive_id: str,
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()

    drive = await get_drive_or_404(db, drive_id)

    if drive.get("status") != "open":
        raise HTTPException(
            status_code=400,
            detail="This drive is not currently open for applications"
        )

    student_id = str(current_user["_id"])

    student = await db.students.find_one(
        {"user_id": student_id}
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    existing = await db.applications.find_one(
        {
            "student_id": student_id,
            "drive_id": drive_id,
        }
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already applied to this drive"
        )

    eligible, reasons = check_eligibility(
        student,
        drive
    )

    if not eligible:
        raise HTTPException(
            status_code=400,
            detail=(
                "You are not eligible for this drive: "
                + "; ".join(reasons)
            ),
        )

    # ---------------------------------------------------------
    # Create recruiter-selected round pipeline
    # ---------------------------------------------------------

    rounds = build_application_rounds(drive)

    application = {
        "student_id": student_id,
        "drive_id": drive_id,
        "status": "applied",
        "applied_at": datetime.now(timezone.utc),

        # New placement pipeline
        "rounds": rounds,

        "eligibility_snapshot": {
            "branch": student.get("branch"),
            "cgpa": student.get("cgpa"),
            "backlogs": student.get("backlogs"),
            "skills": student.get("skills"),
            "certifications": student.get("certifications"),
        },
    }

    result = await db.applications.insert_one(
        application
    )

    application["_id"] = result.inserted_id

    await create_notification(
        db,
        drive["recruiter_id"],
        "New Application",
        (
            f"{current_user['name']} applied for "
            f"{drive['job_title']}"
        ),
    )

    return {
        "success": True,
        "message": "Application submitted",
        "data": application_out(application),
    }


# ---------------------------------------------------------------------------
# Student - My Applications
# ---------------------------------------------------------------------------

@router.get("/mine")
async def list_my_applications(
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()

    student_id = str(current_user["_id"])

    cursor = (
        db.applications
        .find({"student_id": student_id})
        .sort("applied_at", -1)
    )

    results = []

    async for app_doc in cursor:

        try:
            drive = await db.drives.find_one(
                {"_id": ObjectId(app_doc["drive_id"])}
            )
        except (InvalidId, TypeError):
            drive = None

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

        # ---------------------------------------------------------
        # Backward compatibility for old applications
        # ---------------------------------------------------------

        if "rounds" not in out:
            out["rounds"] = build_application_rounds(
                drive or {}
            )

        results.append(out)

    return {
        "success": True,
        "message": "Applications fetched",
        "data": results,
    }


# ---------------------------------------------------------------------------
# Recruiter - Applicants for Drive
# ---------------------------------------------------------------------------

@router.get("/drive/{drive_id}")
async def list_applicants_for_drive(
    drive_id: str,
    current_user: dict = Depends(require_role("recruiter")),
):
    db = get_db()

    drive = await get_drive_or_404(
        db,
        drive_id
    )

    if drive["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You do not own this drive"
        )

    cursor = (
        db.applications
        .find({"drive_id": drive_id})
        .sort("applied_at", -1)
    )

    results = []

    async for app_doc in cursor:

        student = await db.students.find_one(
            {"user_id": app_doc["student_id"]}
        )

        try:
            user_doc = await db.users.find_one(
                {"_id": ObjectId(app_doc["student_id"])}
            )
        except (InvalidId, TypeError):
            user_doc = None

        out = application_out(app_doc)

        # ---------------------------------------------------------
        # Backward compatibility
        # ---------------------------------------------------------

        if "rounds" not in out:
            out["rounds"] = build_application_rounds(
                drive
            )

        out["student"] = {
            "name": user_doc["name"] if user_doc else None,
            "email": user_doc["email"] if user_doc else None,
            "branch": student.get("branch") if student else None,
            "cgpa": student.get("cgpa") if student else None,
            "resume_url": (
                student.get("resume_url")
                if student
                else None
            ),
        }

        results.append(out)

    return {
        "success": True,
        "message": "Applicants fetched",
        "data": results,
    }


# ---------------------------------------------------------------------------
# Recruiter - Update Overall Application Status
# ---------------------------------------------------------------------------

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
        raise HTTPException(
            status_code=400,
            detail="Invalid application id"
        )

    app_doc = await db.applications.find_one(
        {"_id": oid}
    )

    if not app_doc:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    try:
        drive = await db.drives.find_one(
            {"_id": ObjectId(app_doc["drive_id"])}
        )
    except (InvalidId, TypeError):
        drive = None

    if (
        not drive
        or drive["recruiter_id"] != str(current_user["_id"])
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not own the drive for this application"
        )

    await db.applications.update_one(
        {"_id": oid},
        {
            "$set": {
                "status": payload.status.value
            }
        },
    )

    updated = await db.applications.find_one(
        {"_id": oid}
    )

    await create_notification(
        db,
        app_doc["student_id"],
        "Application Status Updated",
        (
            f"Your application for {drive['job_title']} "
            f"at {drive['company_name']} is now "
            f"'{payload.status.value}'"
        ),
    )

    return {
        "success": True,
        "message": "Application status updated",
        "data": application_out(updated),
    }


# ---------------------------------------------------------------------------
# Recruiter - Update Placement Round
# ---------------------------------------------------------------------------

@router.patch("/{application_id}/round")
async def update_application_round(
    application_id: str,
    payload: RoundStatusUpdate,
    current_user: dict = Depends(require_role("recruiter")),
):
    """
    Recruiter evaluates the currently unlocked round.

    Example:

    {
        "round_number": 1,
        "status": "passed",
        "score": 82,
        "feedback": "Good technical knowledge"
    }

    If round 1 passes:

        Technical Interview -> passed
        HR Interview        -> pending

    If round 1 fails:

        Technical Interview -> failed
        HR Interview        -> locked
    """

    db = get_db()

    try:
        oid = ObjectId(application_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid application id"
        )

    app_doc = await db.applications.find_one(
        {"_id": oid}
    )

    if not app_doc:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    try:
        drive = await db.drives.find_one(
            {"_id": ObjectId(app_doc["drive_id"])}
        )
    except (InvalidId, TypeError):
        drive = None

    if (
        not drive
        or drive["recruiter_id"] != str(current_user["_id"])
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not own the drive for this application"
        )

    rounds = app_doc.get("rounds") or build_application_rounds(
        drive
    )

    # round_number is 1-based for easier frontend use
    round_index = payload.round_number - 1

    if round_index < 0 or round_index >= len(rounds):
        raise HTTPException(
            status_code=400,
            detail="Invalid round number"
        )

    # ---------------------------------------------------------
    # Update the round
    # ---------------------------------------------------------

    updated_rounds = update_round_pipeline(
        rounds=rounds,
        round_index=round_index,
        status=payload.status.value,
        score=payload.score,
        feedback=payload.feedback,
    )

    # ---------------------------------------------------------
    # Determine overall application status
    # ---------------------------------------------------------

    new_application_status = app_doc.get(
        "status",
        "applied"
    )

    current_round = updated_rounds[round_index]

    if payload.status.value == "failed":
        new_application_status = "rejected"

    elif payload.status.value == "passed":

        # If there is another round, student is shortlisted
        if round_index < len(updated_rounds) - 1:
            new_application_status = "shortlisted"

        # If this was the final round, student is selected
        else:
            new_application_status = "selected"

    await db.applications.update_one(
        {"_id": oid},
        {
            "$set": {
                "rounds": updated_rounds,
                "status": new_application_status,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    updated = await db.applications.find_one(
        {"_id": oid}
    )

    # ---------------------------------------------------------
    # Student notification
    # ---------------------------------------------------------

    student_round_name = current_round.get(
        "name",
        f"Round {payload.round_number}"
    )

    if payload.status.value == "passed":

        if round_index < len(updated_rounds) - 1:
            next_round = updated_rounds[round_index + 1]

            message = (
                f"You passed {student_round_name} "
                f"for {drive['job_title']} at "
                f"{drive['company_name']}. "
                f"Your next round, {next_round['name']}, "
                f"is now unlocked."
            )
        else:
            message = (
                f"Congratulations! You passed the final round "
                f"({student_round_name}) for "
                f"{drive['job_title']} at "
                f"{drive['company_name']}."
            )

    else:
        message = (
            f"You did not pass {student_round_name} "
            f"for {drive['job_title']} at "
            f"{drive['company_name']}."
        )

    await create_notification(
        db,
        app_doc["student_id"],
        "Placement Round Updated",
        message,
    )

    return {
        "success": True,
        "message": "Placement round updated",
        "data": application_out(updated),
    }


# ---------------------------------------------------------------------------
# Placement Officer - All Applications
# ---------------------------------------------------------------------------

@router.get("/all")
async def list_all_applications(
    current_user: dict = Depends(
        require_role("placement_officer")
    ),
):
    db = get_db()

    cursor = (
        db.applications
        .find({})
        .sort("applied_at", -1)
    )

    results = []

    async for app_doc in cursor:

        try:
            drive = await db.drives.find_one(
                {"_id": ObjectId(app_doc["drive_id"])}
            )
        except (InvalidId, TypeError):
            drive = None

        try:
            user_doc = await db.users.find_one(
                {"_id": ObjectId(app_doc["student_id"])}
            )
        except (InvalidId, TypeError):
            user_doc = None

        out = application_out(app_doc)

        out["drive_title"] = (
            drive["job_title"]
            if drive
            else "Unknown"
        )

        out["company_name"] = (
            drive["company_name"]
            if drive
            else "Unknown"
        )

        out["student_name"] = (
            user_doc["name"]
            if user_doc
            else "Unknown"
        )

        results.append(out)

    return {
        "success": True,
        "message": "All applications fetched",
        "data": results,
    }