"""
Student Readiness Score endpoints, mounted at /api/readiness (see main.py).

  GET  /api/readiness/me                      student: own score
  POST /api/readiness/me/analysis             student: feedback on own score
  GET  /api/readiness/student/{id}            officer: one student's score
  POST /api/readiness/student/{id}/analysis   officer: feedback
  GET  /api/readiness/overview                officer: cohort summary + students needing attention

The score itself comes from app/services/ai/readiness_service.py (explainable, rule-based).
The feedback text comes from our own trained placement model
(app/services/ai/prediction_service.py) plus template-based advice
(app/services/ai/feedback_service.py). It is free, offline and needs no API key.
"""
import hashlib
import json
import logging
import re
from collections import defaultdict
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_current_user
from app.database import get_db
from app.routes.officer import LINK_KEYS, records_for_student, require_officer
from app.services.ai.feedback_service import build_feedback
from app.services.ai.prediction_service import ModelNotTrainedError, predict_placement
from app.services.ai.readiness_service import BANDS, compute_readiness, demand_counter, label_of

router = APIRouter()
logger = logging.getLogger(__name__)

SKILL_FIELDS = ("required_skills", "skills", "skills_required")


def require_student(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "student":
        raise HTTPException(status_code=403, detail="This view is for students")
    return current_user


# ---------------------------------------------------------------------------
# Loading the data the score needs
# ---------------------------------------------------------------------------

async def load_market_skills(db, existing: set):
    """Which skills open drives ask for (used to check a student's skills against demand)."""
    if "drives" not in existing:
        return None
    lists = []
    async for d in db.drives.find({}).sort("_id", -1).limit(200):
        for field in SKILL_FIELDS:
            val = d.get(field)
            if isinstance(val, str):
                val = [p for p in re.split(r"[,;/]", val)]
            if isinstance(val, list):
                lists.append(val)
    return demand_counter(lists)


def features_from(student: dict, counts: dict, market) -> dict:
    return {
        "cgpa": student.get("cgpa"),
        "backlogs": student.get("backlogs", 0),
        "skills": student.get("skills", []),
        "projects": student.get("projects", []),
        "certifications": student.get("certifications", []),
        "resume_url": student.get("resume_url"),
        "profile_completed": student.get("profile_completed", False),
        "applications": counts.get("applications"),
        "interviews": counts.get("interviews"),
        "offers": counts.get("offers"),
        "engagement_known": counts.get("known", True),
        "market_skills": market,
    }


async def student_counts(db, user_id: str, student: dict, existing: set) -> dict:
    ids = [user_id, ObjectId(user_id)]
    if student.get("_id") is not None:
        ids += [str(student["_id"]), student["_id"]]

    apps = await records_for_student(db, "applications", ids, existing)
    interviews = await records_for_student(db, "interviews", ids, existing)
    offers = await records_for_student(db, "offers", ids, existing)

    known = apps is not None  # applications decide whether activity can be scored
    return {
        "applications": len(apps or []),
        "interviews": len(interviews or []),
        "offers": len(offers or []),
        "known": known,
    }


async def build_for_user(db, user: dict) -> dict:
    user_id = str(user["_id"])
    student = await db.students.find_one({"user_id": user_id}) or {}
    existing = set(await db.list_collection_names())
    counts = await student_counts(db, user_id, student, existing)
    market = await load_market_skills(db, existing)
    result = compute_readiness(features_from(student, counts, market))
    result["student"] = {
        "id": user_id,
        "name": user.get("name", ""),
        "branch": student.get("branch"),
    }
    result["facts"] = {
        "cgpa": student.get("cgpa"),
        "backlogs": student.get("backlogs", 0),
        "skills": len([s for s in student.get("skills", []) if label_of(s)]),
        "projects": len([s for s in student.get("projects", []) if label_of(s)]),
        "certifications": len([s for s in student.get("certifications", []) if label_of(s)]),
        "has_resume": bool(student.get("resume_url")),
        "profile_completed": bool(student.get("profile_completed", False)),
        "applications": counts["applications"],
        "interviews": counts["interviews"],
        "offers": counts["offers"],
    }
    return result


# ---------------------------------------------------------------------------
# Single student
# ---------------------------------------------------------------------------

def analysis_payload(result: dict, audience: str = "officer") -> dict:
    """Scores and counts only: no name, no email."""
    return {
        "audience": audience,
        "branch": result["student"].get("branch"),
        "score": result["score"],
        "band": result["band_label"],
        "has_offer": result["has_offer"],
        "components": [
            {"label": c["label"], "score": c["score"], "max": c["max"], "detail": c["detail"]}
            for c in result["components"]
        ],
        "facts": result["facts"],
        "strengths": result["strengths"],
        "gaps": result["gaps"],
        "recommendations": [
            {"title": r["title"], "detail": r["detail"], "points": r["potential"]}
            for r in result["recommendations"]
        ],
    }


def payload_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


async def cached_analysis(db, user_id: str, digest: str, audience: str):
    doc = await db.readiness_analyses.find_one({"user_id": user_id, "audience": audience})
    if doc and doc.get("payload_hash") == digest:
        created = doc.get("created_at")
        return {
            "summary": doc["summary"],
            "model": doc.get("model"),
            "generated_at": created.replace(tzinfo=timezone.utc).isoformat() if created else None,
        }
    return None


async def readiness_response(db, user: dict, audience: str) -> dict:
    result = await build_for_user(db, user)
    digest = payload_hash(analysis_payload(result, audience))
    result["analysis"] = await cached_analysis(db, str(user["_id"]), digest, audience)
    result["ai_available"] = True  # feedback now comes from our own model, no API key needed
    return {"success": True, "message": "Readiness calculated", "data": result}


@router.get("/me")
async def my_readiness(current_user: dict = Depends(require_student)):
    return await readiness_response(get_db(), current_user, "student")


@router.get("/student/{user_id}")
async def student_readiness(user_id: str, _: dict = Depends(require_officer)):
    db = get_db()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404, detail="Student not found")
    user = await db.users.find_one({"_id": ObjectId(user_id), "role": "student"})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    return await readiness_response(db, user, "officer")


# ---------------------------------------------------------------------------
# Feedback from our own model (free, offline)
# ---------------------------------------------------------------------------

async def generate_analysis(db, user: dict, audience: str) -> dict:
    """Feedback from our own trained model + templates. Free, offline, no API key."""
    result = await build_for_user(db, user)
    facts = result["facts"]

    profile = {
        "cgpa": facts.get("cgpa") or 0,
        "active_backlogs": facts.get("backlogs") or 0,
        "skills_count": facts.get("skills") or 0,
        "projects_count": facts.get("projects") or 0,
        "certifications_count": facts.get("certifications") or 0,
        "internships_count": 0,  # no internships field in the data yet
        "has_resume": bool(facts.get("has_resume")),
        "applications_count": facts.get("applications") or 0,
    }

    try:
        prediction = predict_placement(profile)
    except ModelNotTrainedError:
        logger.warning("Placement model not trained; building feedback without a prediction")
        prediction = None

    text = build_feedback(profile, prediction)

    return {
        "summary": text,
        "model": "campuslink-placement-model",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cached": False,
    }


@router.post("/me/analysis")
async def my_analysis(current_user: dict = Depends(require_student)):
    data = await generate_analysis(get_db(), current_user, "student")
    return {"success": True, "message": "Analysis ready", "data": data}


@router.post("/student/{user_id}/analysis")
async def student_analysis(user_id: str, _: dict = Depends(require_officer)):
    db = get_db()
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404, detail="Student not found")
    user = await db.users.find_one({"_id": ObjectId(user_id), "role": "student"})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    data = await generate_analysis(db, user, "officer")
    return {"success": True, "message": "Analysis ready", "data": data}


# ---------------------------------------------------------------------------
# Cohort overview (officer dashboard)
# ---------------------------------------------------------------------------

async def bulk_counts(db, collection: str, id_to_user: dict, existing: set):
    """Counts records per student for a whole cohort in one query. Returns (counts, known)."""
    if collection not in existing:
        return {}, False
    sample = await db[collection].find_one({})
    if sample is None:
        return {}, True
    key = next((k for k in LINK_KEYS if k in sample), None)
    if key is None:
        return {}, False

    wanted = []
    for raw in id_to_user:
        wanted.append(raw)
        if ObjectId.is_valid(raw):
            wanted.append(ObjectId(raw))

    counts: dict = defaultdict(int)
    async for doc in db[collection].find({key: {"$in": wanted}}, {key: 1}):
        user_id = id_to_user.get(str(doc.get(key)))
        if user_id:
            counts[user_id] += 1
    return counts, True


@router.get("/overview")
async def readiness_overview(limit: int = Query(2000, ge=1, le=5000), _: dict = Depends(require_officer)):
    db = get_db()
    existing = set(await db.list_collection_names())

    users = {str(u["_id"]): u async for u in db.users.find({"role": "student"}).limit(limit)}
    students = {s["user_id"]: s async for s in db.students.find({"user_id": {"$in": list(users)}})}

    # any id a record might use for a student -> that student's user id
    id_to_user = {}
    for uid in users:
        id_to_user[uid] = uid
        sid = students.get(uid, {}).get("_id")
        if sid is not None:
            id_to_user[str(sid)] = uid

    apps, apps_known = await bulk_counts(db, "applications", id_to_user, existing)
    interviews, _i = await bulk_counts(db, "interviews", id_to_user, existing)
    offers, _o = await bulk_counts(db, "offers", id_to_user, existing)
    market = await load_market_skills(db, existing)

    bands = {key: 0 for _, key, _ in BANDS}
    bands["offer"] = 0
    branch_scores: dict = defaultdict(list)
    scored = []

    for uid, user in users.items():
        student = students.get(uid, {})
        counts = {
            "applications": apps.get(uid, 0),
            "interviews": interviews.get(uid, 0),
            "offers": offers.get(uid, 0),
            "known": apps_known,
        }
        result = compute_readiness(features_from(student, counts, market))
        branch = student.get("branch") or "Not set"

        if result["has_offer"]:
            bands["offer"] += 1
        else:
            bands[result["band"]] += 1
        branch_scores[branch].append(result["score"])
        scored.append({
            "id": uid,
            "name": user.get("name", ""),
            "branch": student.get("branch"),
            "score": result["score"],
            "band": result["band"],
            "band_label": result["band_label"],
            "has_offer": result["has_offer"],
            "top_gap": result["gaps"][0] if result["gaps"] else None,
        })

    total = len(scored)
    average = round(sum(s["score"] for s in scored) / total, 1) if total else 0

    by_branch = [
        {"branch": b, "average": round(sum(v) / len(v), 1), "count": len(v)}
        for b, v in branch_scores.items()
    ]
    by_branch.sort(key=lambda r: r["average"], reverse=True)

    attention = sorted((s for s in scored if not s["has_offer"]), key=lambda s: s["score"])[:8]

    return {
        "success": True,
        "message": "Readiness overview",
        "data": {
            "total": total,
            "average": average,
            "bands": bands,
            "by_branch": by_branch,
            "attention": attention,
            "activity_tracked": apps_known,
            "market_data": bool(market),
        },
    }