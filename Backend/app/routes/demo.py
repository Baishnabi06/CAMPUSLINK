from fastapi import APIRouter, Depends
from app.core.deps import require_role

router = APIRouter()


@router.get("/student-only")
async def student_only(current_user: dict = Depends(require_role("student"))):
    return {
        "success": True,
        "message": f"Hello student {current_user['name']}, this route is student-only",
        "data": {},
    }


@router.get("/recruiter-only")
async def recruiter_only(current_user: dict = Depends(require_role("recruiter"))):
    return {
        "success": True,
        "message": f"Hello recruiter {current_user['name']}, this route is recruiter-only",
        "data": {},
    }


@router.get("/officer-only")
async def officer_only(
    current_user: dict = Depends(require_role("placement_officer")),
):
    return {
        "success": True,
        "message": f"Hello officer {current_user['name']}, this route is officer-only",
        "data": {},
    }