"""
Free, offline "AI feedback" text built from templates.

Never fails, never needs an API key, never hits a rate limit. Use it as the
default, or as the fallback when an external LLM (Groq etc.) errors out.

Usage:
    from app.services.ai.feedback_service import build_feedback
    text = build_feedback(profile, prediction)   # prediction from predict_placement()
"""


def build_feedback(profile: dict, prediction: dict | None = None) -> str:
    cgpa = float(profile.get("cgpa", 0) or 0)
    backlogs = int(profile.get("active_backlogs", 0) or 0)
    skills = int(profile.get("skills_count", 0) or 0)
    projects = int(profile.get("projects_count", 0) or 0)
    certs = int(profile.get("certifications_count", 0) or 0)
    internships = int(profile.get("internships_count", 0) or 0)
    has_resume = bool(profile.get("has_resume", False))
    applications = int(profile.get("applications_count", 0) or 0)

    parts = []

    # Opening: overall picture
    if prediction:
        band, pct = prediction["band"], prediction["percent"]
        if band == "High":
            parts.append(f"You are in a strong position, with an estimated {pct}% placement chance.")
        elif band == "Moderate":
            parts.append(f"You are on a good track, with an estimated {pct}% placement chance and clear room to grow.")
        else:
            parts.append(f"Your estimated placement chance is {pct}% right now, but every factor in your profile is something you can improve.")
    else:
        parts.append("Here is a quick read of your profile.")

    # What is working
    wins = []
    if cgpa >= 8.0:
        wins.append(f"your CGPA of {cgpa:g}")
    if backlogs == 0:
        wins.append("a clean record with no backlogs")
    if projects >= 3:
        wins.append(f"{projects} projects")
    if certs >= 2:
        wins.append(f"{certs} certifications")
    if internships >= 1:
        wins.append("internship experience")
    if wins:
        parts.append("What is helping you most: " + ", ".join(wins) + ".")

    # Highest-impact fixes, in priority order (max 3)
    actions = []
    if not has_resume:
        actions.append("upload your resume, since recruiters cannot shortlist you without it")
    if backlogs > 0:
        actions.append(f"clear your {backlogs} active backlog(s), as many companies filter on this")
    if applications == 0:
        actions.append("apply to at least a few open drives to start building interview experience")
    if skills < 6:
        actions.append("add more of the tools and technologies you actually use to your skills list")
    if internships == 0:
        actions.append("look for an internship or a real-world project, which employers value highly")
    if projects < 3:
        actions.append("build one or two more projects and describe them clearly on your profile")
    if certs < 2:
        actions.append("complete a relevant certification in a skill that open drives ask for")

    if actions:
        top = actions[:3]
        parts.append("Your best next steps: " + "; ".join(top) + ".")
    else:
        parts.append("Keep your profile up to date and keep applying to drives that match your skills.")

    return " ".join(parts)
