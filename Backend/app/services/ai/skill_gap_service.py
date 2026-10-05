"""
Skill Gap Analysis Service

Compares a student's current skills with the skills required
for a selected placement/job role.
"""

# Skills required for different job roles.
# We can expand this later using your placement dataset / ML.
ROLE_SKILLS = {
    "software engineer": [
        "python",
        "java",
        "c++",
        "javascript",
        "html",
        "css",
        "sql",
        "dsa",
        "git",
        "react"
    ],

    "data scientist": [
        "python",
        "sql",
        "statistics",
        "machine learning",
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "data visualization"
    ],

    "web developer": [
        "html",
        "css",
        "javascript",
        "react",
        "node.js",
        "express",
        "sql",
        "git"
    ],

    "frontend developer": [
        "html",
        "css",
        "javascript",
        "react",
        "responsive design",
        "git"
    ],

    "backend developer": [
        "python",
        "node.js",
        "express",
        "fastapi",
        "sql",
        "mongodb",
        "rest api",
        "git"
    ],

    "data analyst": [
        "python",
        "sql",
        "excel",
        "power bi",
        "statistics",
        "pandas",
        "data visualization"
    ]
}


def normalize_skill(skill: str) -> str:
    """
    Converts a skill into a standard format.
    """

    return skill.strip().lower()


def get_required_skills(target_role: str) -> list:
    """
    Returns the skills required for a particular job role.
    """

    role = normalize_skill(target_role)

    return ROLE_SKILLS.get(role, [])


def calculate_skill_gap(
    student_skills: list,
    target_role: str
) -> dict:
    """
    Compares student skills with the required skills
    for the selected target role.
    """

    # Normalize student skills
    student_skills_normalized = {
        normalize_skill(skill)
        for skill in student_skills
        if skill
    }

    # Get required skills
    required_skills = get_required_skills(target_role)

    required_skills_set = set(required_skills)

    # Skills student already has
    matched_skills = sorted(
        student_skills_normalized & required_skills_set
    )

    # Skills student is missing
    missing_skills = sorted(
        required_skills_set - student_skills_normalized
    )

    # Calculate match percentage
    if required_skills_set:
        match_percentage = round(
            (len(matched_skills) / len(required_skills_set)) * 100
        )
    else:
        match_percentage = 0

    # Generate recommendations
    recommendations = generate_recommendations(missing_skills)

    return {
        "target_role": target_role,
        "match_percentage": match_percentage,
        "total_required_skills": len(required_skills_set),
        "matched_count": len(matched_skills),
        "missing_count": len(missing_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations
    }


def generate_recommendations(missing_skills: list) -> list:
    """
    Generates learning recommendations based on
    the missing skills.
    """

    recommendations = []

    priority_skills = {
        "dsa": "Practice Data Structures and Algorithms regularly.",
        "python": "Learn Python fundamentals and solve coding problems.",
        "java": "Learn Java fundamentals and object-oriented programming.",
        "javascript": "Strengthen JavaScript fundamentals and ES6 concepts.",
        "react": "Learn React components, hooks, state and API integration.",
        "sql": "Practice SQL queries, joins, grouping and database design.",
        "machine learning": "Learn supervised and unsupervised machine learning algorithms.",
        "statistics": "Study probability, statistics and data interpretation.",
        "pandas": "Learn Pandas for data cleaning and data analysis.",
        "numpy": "Learn NumPy arrays and numerical operations.",
        "git": "Learn Git commands, branching and GitHub workflows.",
        "html": "Learn semantic HTML and accessible page structure.",
        "css": "Improve CSS layouts, Flexbox, Grid and responsive design.",
        "power bi": "Learn Power BI dashboards, data modeling and visualization.",
        "mongodb": "Learn MongoDB collections, queries and aggregation.",
        "rest api": "Learn REST API concepts, HTTP methods and JSON.",
        "fastapi": "Learn FastAPI routing, validation and API development."
    }

    for skill in missing_skills:
        recommendation = priority_skills.get(
            skill,
            f"Learn and practice {skill}."
        )

        recommendations.append({
            "skill": skill,
            "recommendation": recommendation
        })

    return recommendations