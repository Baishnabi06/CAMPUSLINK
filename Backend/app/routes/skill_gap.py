"""
Skill Gap Analysis Routes
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.skill_gap_service import (
    calculate_skill_gap,
    ROLE_SKILLS,
)

router = APIRouter()


class SkillGapRequest(BaseModel):
    student_skills: List[str]
    target_role: str


@router.post("/analyze")
async def analyze_skill_gap(request: SkillGapRequest):
    if not request.student_skills:
        raise HTTPException(status_code=400, detail="Student skills cannot be empty.")
    if not request.target_role.strip():
        raise HTTPException(status_code=400, detail="Target role is required.")

    # Normalize: handle comma-separated string accidentally passed as one item
    skills = []
    for s in request.student_skills:
        if "," in s:
            skills.extend([x.strip() for x in s.split(",") if x.strip()])
        else:
            if s.strip():
                skills.append(s.strip())

    result = calculate_skill_gap(student_skills=skills, target_role=request.target_role)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"success": True, "data": result}


@router.get("/roles")
async def get_available_roles():
    return {"success": True, "data": list(ROLE_SKILLS.keys())}