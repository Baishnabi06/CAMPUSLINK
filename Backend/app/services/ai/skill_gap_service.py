"""
Enhanced Skill Gap Analysis Service

Provides accurate skill gap analysis with:
- Proficiency levels (beginner, intermediate, advanced)
- Skill prerequisites and dependencies
- Learning path recommendations
- Resource suggestions
- Time estimates for learning
- Skill categories and domains
- Severity and priority assessment
"""

from enum import Enum
from typing import List, Dict, Tuple
from dataclasses import dataclass


class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Skill:
    name: str
    category: str
    domain: str
    required_level: ProficiencyLevel
    importance_weight: float  # 0.5 to 1.5 (1.0 is normal)
    prerequisites: List[str]  # Other skills needed first
    learning_time_hours: int  # Estimated hours to reach required level
    resources: List[Dict[str, str]]  # [{name, url, type}]


# Comprehensive skill database with metadata
SKILL_DATABASE = {
    # === Core Programming Languages ===
    "python": Skill(
        name="Python",
        category="Programming Language",
        domain="Backend & Data",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.4,
        prerequisites=[],
        learning_time_hours=120,
        resources=[
            {"name": "Python Official Docs", "url": "https://docs.python.org", "type": "documentation"},
            {"name": "Real Python", "url": "https://realpython.com", "type": "tutorial"},
            {"name": "LeetCode", "url": "https://leetcode.com", "type": "practice"},
        ]
    ),
    "java": Skill(
        name="Java",
        category="Programming Language",
        domain="Backend & Enterprise",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["dsa"],
        learning_time_hours=140,
        resources=[
            {"name": "Oracle Java Docs", "url": "https://docs.oracle.com/javase", "type": "documentation"},
            {"name": "Codecademy Java", "url": "https://codecademy.com", "type": "course"},
        ]
    ),
    "javascript": Skill(
        name="JavaScript",
        category="Programming Language",
        domain="Frontend & Full-stack",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.4,
        prerequisites=[],
        learning_time_hours=100,
        resources=[
            {"name": "MDN Web Docs", "url": "https://developer.mozilla.org", "type": "documentation"},
            {"name": "JavaScript.info", "url": "https://javascript.info", "type": "tutorial"},
        ]
    ),
    "c++": Skill(
        name="C++",
        category="Programming Language",
        domain="Systems & Performance",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.1,
        prerequisites=["dsa"],
        learning_time_hours=160,
        resources=[
            {"name": "cppreference", "url": "https://en.cppreference.com", "type": "documentation"},
            {"name": "LeetCode C++", "url": "https://leetcode.com", "type": "practice"},
        ]
    ),

    # === Foundational Skills ===
    "dsa": Skill(
        name="Data Structures & Algorithms",
        category="Foundational",
        domain="Core CS",
        required_level=ProficiencyLevel.ADVANCED,
        importance_weight=1.5,
        prerequisites=[],
        learning_time_hours=200,
        resources=[
            {"name": "LeetCode", "url": "https://leetcode.com", "type": "practice"},
            {"name": "GeeksforGeeks DSA", "url": "https://geeksforgeeks.org", "type": "tutorial"},
            {"name": "MIT OpenCourseWare", "url": "https://ocw.mit.edu", "type": "course"},
        ]
    ),
    "system design": Skill(
        name="System Design",
        category="Foundational",
        domain="Architecture",
        required_level=ProficiencyLevel.ADVANCED,
        importance_weight=1.3,
        prerequisites=["dsa", "database design"],
        learning_time_hours=150,
        resources=[
            {"name": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "guide"},
        ]
    ),

    # === Web Frontend ===
    "html": Skill(
        name="HTML",
        category="Frontend",
        domain="Web",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.0,
        prerequisites=[],
        learning_time_hours=40,
        resources=[
            {"name": "MDN HTML", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML", "type": "documentation"},
        ]
    ),
    "css": Skill(
        name="CSS",
        category="Frontend",
        domain="Web",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.0,
        prerequisites=["html"],
        learning_time_hours=60,
        resources=[
            {"name": "MDN CSS", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS", "type": "documentation"},
            {"name": "CSS Tricks", "url": "https://css-tricks.com", "type": "guide"},
        ]
    ),
    "react": Skill(
        name="React",
        category="Frontend",
        domain="Frontend Framework",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.3,
        prerequisites=["javascript", "html", "css"],
        learning_time_hours=80,
        resources=[
            {"name": "React Official Docs", "url": "https://react.dev", "type": "documentation"},
            {"name": "React Tutorial", "url": "https://react.dev/learn", "type": "tutorial"},
        ]
    ),
    "vue.js": Skill(
        name="Vue.js",
        category="Frontend",
        domain="Frontend Framework",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.1,
        prerequisites=["javascript", "html", "css"],
        learning_time_hours=70,
        resources=[
            {"name": "Vue Official Docs", "url": "https://vuejs.org", "type": "documentation"},
        ]
    ),
    "responsive design": Skill(
        name="Responsive Design",
        category="Frontend",
        domain="UI/UX",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.1,
        prerequisites=["html", "css"],
        learning_time_hours=50,
        resources=[
            {"name": "MDN Responsive Design", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design", "type": "guide"},
        ]
    ),

    # === Backend & Databases ===
    "node.js": Skill(
        name="Node.js",
        category="Backend Runtime",
        domain="Full-stack",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["javascript"],
        learning_time_hours=80,
        resources=[
            {"name": "Node.js Official Docs", "url": "https://nodejs.org/docs", "type": "documentation"},
        ]
    ),
    "express": Skill(
        name="Express.js",
        category="Backend Framework",
        domain="Full-stack",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["node.js"],
        learning_time_hours=60,
        resources=[
            {"name": "Express Official Docs", "url": "https://expressjs.com", "type": "documentation"},
        ]
    ),
    "fastapi": Skill(
        name="FastAPI",
        category="Backend Framework",
        domain="Backend",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["python"],
        learning_time_hours=70,
        resources=[
            {"name": "FastAPI Docs", "url": "https://fastapi.tiangolo.com", "type": "documentation"},
        ]
    ),
    "sql": Skill(
        name="SQL",
        category="Database",
        domain="Data Persistence",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.3,
        prerequisites=[],
        learning_time_hours=80,
        resources=[
            {"name": "SQL Tutorial", "url": "https://www.w3schools.com/sql", "type": "tutorial"},
            {"name": "LeetCode SQL", "url": "https://leetcode.com", "type": "practice"},
        ]
    ),
    "mongodb": Skill(
        name="MongoDB",
        category="Database",
        domain="NoSQL",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.0,
        prerequisites=["json"],
        learning_time_hours=60,
        resources=[
            {"name": "MongoDB University", "url": "https://university.mongodb.com", "type": "course"},
        ]
    ),
    "database design": Skill(
        name="Database Design",
        category="Database",
        domain="Data Architecture",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["sql"],
        learning_time_hours=100,
        resources=[
            {"name": "Database Design Tutorial", "url": "https://www.guru99.com/database-design.html", "type": "guide"},
        ]
    ),

    # === Data & ML ===
    "python data": Skill(
        name="Python for Data",
        category="Data Science",
        domain="Data",
        required_level=ProficiencyLevel.ADVANCED,
        importance_weight=1.3,
        prerequisites=["python"],
        learning_time_hours=100,
        resources=[
            {"name": "Real Python Data Science", "url": "https://realpython.com/learning-paths/data-science/", "type": "guide"},
        ]
    ),
    "pandas": Skill(
        name="Pandas",
        category="Data Science Library",
        domain="Data Processing",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["python"],
        learning_time_hours=60,
        resources=[
            {"name": "Pandas Official Docs", "url": "https://pandas.pydata.org/docs", "type": "documentation"},
        ]
    ),
    "numpy": Skill(
        name="NumPy",
        category="Data Science Library",
        domain="Numerical Computing",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.1,
        prerequisites=["python"],
        learning_time_hours=50,
        resources=[
            {"name": "NumPy Official Docs", "url": "https://numpy.org/doc", "type": "documentation"},
        ]
    ),
    "matplotlib": Skill(
        name="Matplotlib",
        category="Data Visualization",
        domain="Visualization",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=0.9,
        prerequisites=["python", "numpy"],
        learning_time_hours=40,
        resources=[
            {"name": "Matplotlib Tutorial", "url": "https://matplotlib.org/stable/tutorials/index", "type": "tutorial"},
        ]
    ),
    "scikit-learn": Skill(
        name="Scikit-learn",
        category="ML Library",
        domain="Machine Learning",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["python", "numpy", "pandas", "statistics"],
        learning_time_hours=100,
        resources=[
            {"name": "Scikit-learn Docs", "url": "https://scikit-learn.org/stable", "type": "documentation"},
        ]
    ),
    "machine learning": Skill(
        name="Machine Learning",
        category="ML Concepts",
        domain="Machine Learning",
        required_level=ProficiencyLevel.ADVANCED,
        importance_weight=1.4,
        prerequisites=["python", "statistics", "linear algebra"],
        learning_time_hours=150,
        resources=[
            {"name": "Andrew Ng ML Course", "url": "https://www.coursera.org/learn/machine-learning", "type": "course"},
            {"name": "ML Textbook", "url": "https://github.com/fastai", "type": "guide"},
        ]
    ),
    "statistics": Skill(
        name="Statistics",
        category="Mathematics",
        domain="Data Science Foundation",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=[],
        learning_time_hours=120,
        resources=[
            {"name": "Khan Academy Statistics", "url": "https://www.khanacademy.org/math/statistics-probability", "type": "course"},
        ]
    ),
    "linear algebra": Skill(
        name="Linear Algebra",
        category="Mathematics",
        domain="ML Foundation",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=[],
        learning_time_hours=100,
        resources=[
            {"name": "Khan Academy Linear Algebra", "url": "https://www.khanacademy.org/math/linear-algebra", "type": "course"},
        ]
    ),

    # === DevOps & Tools ===
    "git": Skill(
        name="Git & GitHub",
        category="Version Control",
        domain="DevOps",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.1,
        prerequisites=[],
        learning_time_hours=30,
        resources=[
            {"name": "Git Official Docs", "url": "https://git-scm.com/doc", "type": "documentation"},
            {"name": "GitHub Learning", "url": "https://github.skills.github.com", "type": "course"},
        ]
    ),
    "docker": Skill(
        name="Docker",
        category="Containerization",
        domain="DevOps",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.1,
        prerequisites=["git"],
        learning_time_hours=70,
        resources=[
            {"name": "Docker Official Docs", "url": "https://docs.docker.com", "type": "documentation"},
        ]
    ),
    "kubernetes": Skill(
        name="Kubernetes",
        category="Orchestration",
        domain="DevOps",
        required_level=ProficiencyLevel.ADVANCED,
        importance_weight=1.0,
        prerequisites=["docker"],
        learning_time_hours=120,
        resources=[
            {"name": "Kubernetes Official Docs", "url": "https://kubernetes.io/docs", "type": "documentation"},
        ]
    ),
    "rest api": Skill(
        name="REST API Design",
        category="Architecture",
        domain="Backend",
        required_level=ProficiencyLevel.INTERMEDIATE,
        importance_weight=1.2,
        prerequisites=["http basics"],
        learning_time_hours=50,
        resources=[
            {"name": "REST API Best Practices", "url": "https://restfulapi.net", "type": "guide"},
        ]
    ),
    "http basics": Skill(
        name="HTTP & Networking",
        category="Networking",
        domain="Foundation",
        required_level=ProficiencyLevel.BEGINNER,
        importance_weight=1.0,
        prerequisites=[],
        learning_time_hours=30,
        resources=[
            {"name": "MDN HTTP", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP", "type": "documentation"},
        ]
    ),

    # === Data Formats & Other ===
    "json": Skill(
        name="JSON",
        category="Data Format",
        domain="Foundation",
        required_level=ProficiencyLevel.BEGINNER,
        importance_weight=0.8,
        prerequisites=[],
        learning_time_hours=10,
        resources=[
            {"name": "JSON.org", "url": "https://www.json.org", "type": "documentation"},
        ]
    ),
}

# Role-specific skill requirements
ROLE_SKILLS_DETAILED = {
    "software engineer": {
        "essential": ["python", "dsa", "system design", "database design"],
        "frontend": ["javascript", "react", "html", "css"],
        "backend": ["python", "sql", "rest api"],
        "tools": ["git", "docker"],
    },
    "data scientist": {
        "essential": ["python", "statistics", "machine learning"],
        "data_processing": ["pandas", "numpy", "sql"],
        "visualization": ["matplotlib"],
        "ml_libraries": ["scikit-learn"],
    },
    "web developer": {
        "essential": ["javascript", "html", "css"],
        "frontend": ["react", "responsive design"],
        "backend": ["node.js", "express", "sql"],
        "tools": ["git"],
    },
    "frontend developer": {
        "essential": ["javascript", "html", "css", "react"],
        "ui_ux": ["responsive design"],
        "tools": ["git"],
    },
    "backend developer": {
        "essential": ["python", "sql", "rest api", "dsa"],
        "frameworks": ["fastapi", "node.js"],
        "databases": ["mongodb", "database design"],
        "devops": ["git", "docker"],
    },
    "data analyst": {
        "essential": ["sql", "statistics"],
        "tools": ["pandas", "python"],
        "visualization": ["matplotlib"],
    },
    "devops engineer": {
        "essential": ["linux", "docker", "kubernetes"],
        "scripting": ["python", "bash"],
        "tools": ["git"],
    },
}


def normalize_skill(skill: str) -> str:
    """Normalize skill name to lowercase."""
    return skill.strip().lower()


def get_skill_info(skill_name: str) -> Skill:
    """Get skill information from database."""
    normalized = normalize_skill(skill_name)
    return SKILL_DATABASE.get(normalized)


def build_learning_path(missing_skills: List[str], all_skills: Dict[str, Skill]) -> List[Dict]:
    """
    Build optimized learning path based on prerequisites and importance.
    Uses topological sort to ensure prerequisites are learned first.
    """
    path = []
    visited = set()
    temp_visited = set()

    def visit(skill_name: str, path_order: List[Dict]):
        if skill_name in visited:
            return
        if skill_name not in all_skills:
            return

        skill = all_skills[skill_name]

        # Check for circular dependencies
        if skill_name in temp_visited:
            return

        temp_visited.add(skill_name)

        # Visit prerequisites first
        for prereq in skill.prerequisites:
            if prereq in missing_skills and prereq not in visited:
                visit(prereq, path_order)

        temp_visited.remove(skill_name)
        visited.add(skill_name)

        path_order.append({
            "skill": skill.name,
            "skill_key": skill_name,
            "category": skill.category,
            "domain": skill.domain,
            "difficulty": skill.required_level.value,
            "learning_hours": skill.learning_time_hours,
            "resources": skill.resources,
            "prerequisites": [SKILL_DATABASE[p].name for p in skill.prerequisites if p in SKILL_DATABASE],
        })

    # Build path
    for skill in missing_skills:
        visit(skill, path)

    # Sort by priority: importance weight and learning time
    path.sort(key=lambda x: (
        -all_skills[x["skill_key"]].importance_weight,
        all_skills[x["skill_key"]].required_level.value != "beginner"
    ))

    return path


def calculate_skill_gap_advanced(
    student_skills: List[str],
    student_proficiency: Dict[str, str] = None,
    target_role: str = None,
) -> dict:
    """
    Advanced skill gap analysis with proficiency levels, learning paths, and detailed recommendations.

    Args:
        student_skills: List of skill names student has
        student_proficiency: Dict mapping skill names to proficiency levels
        target_role: Target job role

    Returns:
        Comprehensive gap analysis including learning path
    """

    # Normalize student skills
    student_skills_normalized = {normalize_skill(s): s for s in student_skills if s}
    student_proficiency = student_proficiency or {}

    # Get required skills for role
    if not target_role:
        return {"error": "Target role is required"}

    role_key = normalize_skill(target_role)
    if role_key not in ROLE_SKILLS_DETAILED:
        available = list(ROLE_SKILLS_DETAILED.keys())
        return {
            "error": f"Role '{target_role}' not found",
            "available_roles": available
        }

    role_skills_map = ROLE_SKILLS_DETAILED[role_key]

    # Flatten role requirements
    required_skills_list = []
    for category, skills in role_skills_map.items():
        required_skills_list.extend(skills)

    required_skills_set = set(s for s in required_skills_list if normalize_skill(s) in SKILL_DATABASE)

    # Categorize skills
    matched_skills = []
    missing_skills = []
    proficiency_gaps = []  # Skills with insufficient proficiency

    for skill_norm in required_skills_set:
        skill_info = SKILL_DATABASE.get(skill_norm)
        if not skill_info:
            continue

        if skill_norm in student_skills_normalized:
            student_level = student_proficiency.get(skill_norm, "beginner")
            if student_level == skill_info.required_level.value or (
                ["beginner", "intermediate", "advanced", "expert"].index(student_level)
                >= ["beginner", "intermediate", "advanced", "expert"].index(skill_info.required_level.value)
            ):
                matched_skills.append({
                    "skill": skill_info.name,
                    "category": skill_info.category,
                    "current_level": student_level,
                    "required_level": skill_info.required_level.value,
                })
            else:
                proficiency_gaps.append({
                    "skill": skill_info.name,
                    "current_level": student_level,
                    "required_level": skill_info.required_level.value,
                    "gap": skill_info.required_level.value,
                })
        else:
            missing_skills.append(skill_norm)

    # Calculate metrics
    total_required = len(required_skills_set)
    matched_count = len(matched_skills)
    missing_count = len(missing_skills) + len(proficiency_gaps)
    match_percentage = round((matched_count / total_required * 100)) if total_required > 0 else 0

    # Assess severity
    if match_percentage >= 80:
        severity = "low"
        severity_description = "You're well-prepared for this role"
    elif match_percentage >= 60:
        severity = "medium"
        severity_description = "You have a solid foundation, need some skills"
    elif match_percentage >= 40:
        severity = "high"
        severity_description = "Significant skill gaps to address"
    else:
        severity = "critical"
        severity_description = "Major preparation needed"

    # Build learning path
    all_missing_normalized = [normalize_skill(s) for s in missing_skills]
    all_missing_normalized.extend([normalize_skill(s) for s, _ in [(p["skill"].lower(), "") for p in proficiency_gaps]])

    learning_path = build_learning_path(all_missing_normalized, SKILL_DATABASE)

    # Calculate total learning time
    total_hours = sum(item["learning_hours"] for item in learning_path)

    return {
        "success": True,
        "target_role": target_role,
        "match_percentage": match_percentage,
        "severity": severity,
        "severity_description": severity_description,
        "total_required_skills": total_required,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "proficiency_gap_count": len(proficiency_gaps),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "proficiency_gaps": proficiency_gaps,
        "learning_path": learning_path,
        "total_learning_hours": total_hours,
        "estimated_weeks": round(total_hours / 20),  # Assuming 20 hours/week study
        "priority_order": [item["skill"] for item in learning_path[:5]],  # Top 5 to learn first
    }


def get_role_overview(target_role: str) -> dict:
    """Get overview of skills needed for a role."""
    role_key = normalize_skill(target_role)
    if role_key not in ROLE_SKILLS_DETAILED:
        return {"error": f"Role '{target_role}' not found"}

    role_map = ROLE_SKILLS_DETAILED[role_key]
    skills_list = []

    for category, skills in role_map.items():
        for skill_name in skills:
            skill_info = SKILL_DATABASE.get(normalize_skill(skill_name))
            if skill_info:
                skills_list.append({
                    "skill": skill_info.name,
                    "category": skill_info.category,
                    "required_level": skill_info.required_level.value,
                    "importance": skill_info.importance_weight,
                })

    return {
        "role": target_role,
        "total_skills": len(skills_list),
        "skills": skills_list,
        "categories": list(set(s["category"] for s in skills_list)),
    }