"""
Placeholder interface for the AI team's placement-readiness scoring model.
This file defines the CONTRACT the rest of the app expects — do not
implement real scoring logic here. The AI team replaces the function
body only; nothing else in the codebase should need to change when they do.
"""


async def get_readiness_score(student_id: str) -> dict:
    """
    Expected return shape once implemented:
    {
        "score": float,        # 0-100
        "factors": dict,       # contributing factors, model-defined
        "generated_at": str,   # ISO timestamp
    }
    """
    raise NotImplementedError("AI readiness scoring is not yet implemented by the AI team.")