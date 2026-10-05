"""
Improved Skill Gap Analysis Routes

Enhanced endpoints for:
- Detailed skill gap analysis
- Learning path generation
- Role overviews
- Proficiency-aware gap calculation
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.skill_gap_service import (
    calculate_skill_gap_advanced,
    get_role_overview,
    SKILL_DATABASE,
    ROLE_SKILLS_DETAILED,
)

router = APIRouter()


class SkillGapRequest(BaseModel):
    """Request for skill gap analysis."""
    student_skills: List[str]
    student_proficiency: Optional[Dict[str, str]] = None  # skill -> "beginner"|"intermediate"|"advanced"|"expert"
    target_role: str


class RoleOverviewRequest(BaseModel):
    """Request for role overview."""
    target_role: str


@router.post("/analyze")
async def analyze_skill_gap_advanced(request: SkillGapRequest):
    """
    Analyze skill gap with advanced metrics.
    
    Returns:
    - Match percentage
    - Severity assessment
    - Proficiency gaps
    - Optimized learning path
    - Time estimates
    """

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

    result = calculate_skill_gap_advanced(
        student_skills=request.student_skills,
        student_proficiency=request.student_proficiency,
        target_role=request.target_role,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/roles")
async def get_available_roles():
    """Return all available job roles for skill gap analysis."""
    return {
        "success": True,
        "data": list(ROLE_SKILLS_DETAILED.keys()),
        "count": len(ROLE_SKILLS_DETAILED),
    }


@router.post("/role-overview")
async def role_overview(request: RoleOverviewRequest):
    """
    Get detailed overview of skills required for a specific role.
    
    Shows:
    - All required skills
    - Skill categories
    - Required proficiency levels
    - Importance weights
    """

    if not request.target_role.strip():
        raise HTTPException(
            status_code=400,
            detail="Target role is required."
        )

    result = get_role_overview(request.target_role)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "success": True,
        "data": result
    }


@router.get("/skill/{skill_name}")
async def get_skill_details(skill_name: str):
    """
    Get detailed information about a specific skill.
    
    Includes:
    - Description & category
    - Prerequisites
    - Learning resources
    - Time estimate
    - Related skills
    """

    from app.services.ai.skill_gap_service_improved import (
        normalize_skill,
        SKILL_DATABASE,
    )

    skill_normalized = normalize_skill(skill_name)
    skill_info = SKILL_DATABASE.get(skill_normalized)

    if not skill_info:
        raise HTTPException(
            status_code=404,
            detail=f"Skill '{skill_name}' not found"
        )

    return {
        "success": True,
        "data": {
            "name": skill_info.name,
            "category": skill_info.category,
            "domain": skill_info.domain,
            "required_level": skill_info.required_level.value,
            "importance_weight": skill_info.importance_weight,
            "prerequisites": skill_info.prerequisites,
            "learning_time_hours": skill_info.learning_time_hours,
            "learning_time_weeks": round(skill_info.learning_time_hours / 20),
            "resources": skill_info.resources,
        }
    }


@router.get("/comparison")
async def compare_roles(roles: str):
    """
    Compare skills required across multiple roles.
    
    Shows:
    - Common skills
    - Unique skills per role
    - Overlap analysis
    """

    role_list = [r.strip() for r in roles.split(",")]

    if len(role_list) < 2:
        raise HTTPException(
            status_code=400,
            detail="Provide at least 2 roles to compare"
        )

    from app.services.ai.skill_gap_service_improved import normalize_skill

    comparison = {
        "roles": role_list,
        "role_skills": {},
        "common_skills": [],
        "unique_skills": {},
    }

    role_skill_sets = {}

    for role in role_list:
        role_norm = normalize_skill(role)
        if role_norm not in ROLE_SKILLS_DETAILED:
            raise HTTPException(
                status_code=404,
                detail=f"Role '{role}' not found"
            )

        role_map = ROLE_SKILLS_DETAILED[role_norm]
        skills_flat = []
        for category, skills in role_map.items():
            skills_flat.extend(skills)

        role_skill_sets[role] = set(s.lower() for s in skills_flat)
        comparison["role_skills"][role] = list(role_skill_sets[role])
        comparison["unique_skills"][role] = []

    # Find common skills
    if role_skill_sets:
        comparison["common_skills"] = list(
            set.intersection(*role_skill_sets.values())
        )

    # Find unique skills per role
    for role in role_list:
        other_skills = set.union(
            *[skills for r, skills in role_skill_sets.items() if r != role]
        )
        comparison["unique_skills"][role] = list(
            role_skill_sets[role] - other_skills
        )

    return {
        "success": True,
        "data": comparison
    }


@router.post("/learning-recommendations")
async def get_learning_recommendations(request: SkillGapRequest):
    """
    Get personalized learning recommendations based on skill gap.
    
    Provides:
    - Optimized learning sequence
    - Time estimates per skill
    - Resource suggestions
    - Prerequisite guidance
    """

    result = calculate_skill_gap_advanced(
        student_skills=request.student_skills,
        student_proficiency=request.student_proficiency,
        target_role=request.target_role,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    recommendations = {
        "role": request.target_role,
        "severity": result["severity"],
        "total_weeks_to_proficiency": result["estimated_weeks"],
        "top_priorities": result["priority_order"],
        "learning_path": result["learning_path"],
        "quick_wins": [
            item for item in result["learning_path"]
            if item["learning_hours"] < 50
        ][:3],
    }

    return {
        "success": True,
        "data": recommendations
    }