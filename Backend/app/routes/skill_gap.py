from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.skill_gap_service import ROLE_SKILLS, calculate_skill_gap

router = APIRouter()


class SkillGapRequest(BaseModel):
    student_skills: List[str]
    target_role: str


@router.post("/analyze")
async def analyze_skill_gap(request: SkillGapRequest):
    """Compare the student's skills with the skills required for a target role."""

    if not request.student_skills:
        raise HTTPException(
            status_code=400,
            detail="Student skills cannot be empty."
        )

    if not request.target_role.strip():
        raise HTTPException(
            status_code=400,
            detail="Target role is required."
        )

    result = calculate_skill_gap(
        student_skills=request.student_skills,
        target_role=request.target_role,
    )

    if result["total_required_skills"] == 0:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Target role '{request.target_role}' is not available. "
                f"Available roles: {', '.join(ROLE_SKILLS.keys())}"
            ),
        )

    return {
        "success": True,
        "data": result
    }


@router.get("/roles")
async def get_available_roles():
    """Return all job roles available for skill gap analysis."""

    return {
        "success": True,
        "data": list(ROLE_SKILLS.keys())
    }