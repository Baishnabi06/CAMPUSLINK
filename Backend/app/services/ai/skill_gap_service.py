"""
Placeholder interface for the AI team's skill-gap analysis model.
"""


async def get_skill_gap(student_id: str, target_role: str | None = None) -> dict:
    """
    Expected return shape once implemented:
    {
        "missing_skills": list[str],
        "recommended_resources": list[str],
    }
    """
    raise NotImplementedError("AI skill-gap analysis is not yet implemented by the AI team.")