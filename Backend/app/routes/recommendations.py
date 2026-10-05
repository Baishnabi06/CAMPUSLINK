
from fastapi import APIRouter, Depends

from app.database import get_db
from app.core.deps import require_role
from app.services.job_recommender import (
    check_eligibility,
    calculate_match
)


router = APIRouter()


def drive_out(drive: dict) -> dict:
    drive = dict(drive)

    drive["id"] = str(drive["_id"])

    del drive["_id"]

    return drive


@router.get("/jobs")
async def get_recommended_jobs(
    current_user: dict = Depends(
        require_role("student")
    )
):

    db = get_db()

    user_id = str(current_user["_id"])

    # Get logged-in student's profile
    student = await db.students.find_one({
        "user_id": user_id
    })

    if not student:
        return {
            "success": False,
            "message": "Student profile not found",
            "data": []
        }

    # Get all open placement drives
    cursor = db.drives.find({
        "status": "open"
    })

    recommendations = []

    async for drive in cursor:

        # First check basic eligibility
        eligible = check_eligibility(
            student,
            drive
        )

        if not eligible:
            continue

        # AI matching
        match = calculate_match(
            student,
            drive
        )

        recommendations.append({
            "id": str(drive["_id"]),
            "company_name": drive.get(
                "company_name",
                ""
            ),
            "job_title": drive.get(
                "job_title",
                ""
            ),
            "job_description": drive.get(
                "job_description",
                ""
            ),
            "required_skills": drive.get(
                "required_skills",
                []
            ),
            "ctc": drive.get(
                "ctc",
                0
            ),
            "location": drive.get(
                "location"
            ),
            "mode": drive.get(
                "mode"
            ),
            "application_deadline": drive.get(
                "application_deadline"
            ),
            **match
        })

    # Highest match first
    recommendations.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    # Return top 10
    recommendations = recommendations[:10]

    return {
        "success": True,
        "message": "Recommended jobs fetched",
        "data": recommendations
    }