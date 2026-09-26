"""
Placeholder interface for the AI team's recruiter-student matching and
resume / job-description analysis models.
"""


async def match_students_to_drive(drive_id: str) -> list[dict]:
    """
    Expected return shape once implemented:
    [{"student_id": str, "fit_score": float, "reasons": list[str]}, ...]
    """
    raise NotImplementedError("AI candidate matching is not yet implemented by the AI team.")


async def analyze_resume(student_id: str) -> dict:
    """
    Expected return shape once implemented:
    {"parsed_skills": list[str], "summary": str}
    """
    raise NotImplementedError("AI resume analysis is not yet implemented by the AI team.")


async def analyze_job_description(drive_id: str) -> dict:
    """
    Expected return shape once implemented:
    {"extracted_skills": list[str], "seniority_level": str}
    """
    raise NotImplementedError("AI job-description analysis is not yet implemented by the AI team.")