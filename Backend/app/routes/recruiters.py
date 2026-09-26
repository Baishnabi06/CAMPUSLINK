from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import RecruiterProfileUpdate

router = APIRouter()


def recruiter_out(recruiter: dict) -> dict:
    recruiter = dict(recruiter)
    recruiter["id"] = str(recruiter["_id"])
    del recruiter["_id"]
    return recruiter


@router.get("/me")
async def get_my_recruiter_profile(current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    recruiter = await db.recruiters.find_one({"user_id": str(current_user["_id"])})
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")
    return {"success": True, "message": "Recruiter profile fetched", "data": recruiter_out(recruiter)}


@router.put("/me")
async def update_my_recruiter_profile(
    payload: RecruiterProfileUpdate,
    current_user: dict = Depends(require_role("recruiter")),
):
    db = get_db()
    user_id = str(current_user["_id"])
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    result = await db.recruiters.update_one({"user_id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Recruiter profile not found")

    updated = await db.recruiters.find_one({"user_id": user_id})
    return {"success": True, "message": "Company profile updated", "data": recruiter_out(updated)}