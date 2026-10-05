
from typing import Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Lightweight pretrained NLP model
model = SentenceTransformer("all-MiniLM-L6-v2")


def normalize(value: str) -> str:
    return value.strip().lower()


def calculate_skill_score(
    student_skills: list[str],
    required_skills: list[str]
) -> tuple[float, list[str]]:
    if not required_skills:
        return 100.0, []

    student_set = {normalize(skill) for skill in student_skills}
    required_set = {normalize(skill) for skill in required_skills}

    matched = student_set.intersection(required_set)

    score = (len(matched) / len(required_set)) * 100

    return round(score, 2), sorted(matched)


def calculate_certification_score(
    student_certifications: list[str],
    required_certifications: list[str]
) -> float:
    if not required_certifications:
        return 100.0

    student_set = {
        normalize(cert)
        for cert in student_certifications
    }

    required_set = {
        normalize(cert)
        for cert in required_certifications
    }

    matched = student_set.intersection(required_set)

    return round(
        (len(matched) / len(required_set)) * 100,
        2
    )


def calculate_semantic_score(
    student_text: str,
    job_text: str
) -> float:

    if not student_text.strip() or not job_text.strip():
        return 0.0

    embeddings = model.encode(
        [student_text, job_text]
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(float(similarity * 100), 2)


def check_eligibility(
    student: dict[str, Any],
    drive: dict[str, Any]
) -> bool:

    # Branch check
    required_branches = [
        normalize(branch)
        for branch in drive.get("required_branches", [])
    ]

    student_branch = normalize(
        student.get("branch") or ""
    )

    if required_branches:
        if student_branch not in required_branches:
            return False

    # CGPA check
    student_cgpa = student.get("cgpa")

    if student_cgpa is None:
        return False

    min_cgpa = drive.get("min_cgpa", 0)

    if student_cgpa < min_cgpa:
        return False

    # Backlog check
    student_backlogs = student.get("backlogs", 0)

    max_backlogs = drive.get("max_backlogs", 0)

    if student_backlogs > max_backlogs:
        return False

    # Certification check
    required_certifications = drive.get(
        "required_certifications", []
    )

    student_certifications = student.get(
        "certifications", []
    )

    if required_certifications:

        student_certs = {
            normalize(cert)
            for cert in student_certifications
        }

        required_certs = {
            normalize(cert)
            for cert in required_certifications
        }

        if not required_certs.issubset(student_certs):
            return False

    return True


def calculate_match(
    student: dict[str, Any],
    drive: dict[str, Any]
) -> dict[str, Any]:

    student_skills = student.get("skills", [])
    required_skills = drive.get("required_skills", [])

    skill_score, matched_skills = calculate_skill_score(
        student_skills,
        required_skills
    )

    certification_score = calculate_certification_score(
        student.get("certifications", []),
        drive.get("required_certifications", [])
    )

    student_text = " ".join([
        " ".join(student.get("skills", [])),
        " ".join(student.get("projects", [])),
        " ".join(student.get("certifications", []))
    ])

    job_text = " ".join([
        drive.get("job_title", ""),
        drive.get("job_description", ""),
        " ".join(drive.get("required_skills", [])),
        " ".join(drive.get("required_certifications", []))
    ])

    semantic_score = calculate_semantic_score(
        student_text,
        job_text
    )

    # Weighted AI recommendation score
    final_score = (
        skill_score * 0.40
        + semantic_score * 0.40
        + certification_score * 0.20
    )

    return {
        "match_score": round(final_score, 2),
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "certification_score": certification_score,
        "matched_skills": matched_skills
    }