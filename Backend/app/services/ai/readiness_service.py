"""
Student Readiness Score engine.

A transparent, explainable score from 0 to 100 built from six components.
It needs no training data, so it works from day one, and every point can be
traced back to something on the student's profile or activity.

    Academics       25   CGPA (20) + backlogs (5)
    Skills          20   how many skills, and how many are in demand with recruiters
    Projects        15   3 or more projects = full marks
    Certifications  10   2 or more = full marks
    Profile         10   resume uploaded (6) + profile completed (4)
    Engagement      20   applications (12) + interviews (8); an offer = full marks

If application tracking isn't available, Engagement is left out and the score
is rescaled over the remaining components, so nobody is penalised for missing data.
"""
from collections import Counter

WEIGHTS = {
    "academics": 25,
    "skills": 20,
    "projects": 15,
    "certifications": 10,
    "profile": 10,
    "engagement": 20,
}

LABELS = {
    "academics": "Academics",
    "skills": "Skills",
    "projects": "Projects",
    "certifications": "Certifications",
    "profile": "Profile and resume",
    "engagement": "Activity",
}

# (minimum score, key, label)
BANDS = [
    (75, "ready", "Ready"),
    (55, "almost_ready", "Almost ready"),
    (35, "needs_work", "Needs work"),
    (0, "at_risk", "At risk"),
]

CGPA_FLOOR = 5.0   # at or below this, CGPA earns 0 points
CGPA_FULL = 8.5    # at or above this, CGPA earns all 20 points
SKILLS_TARGET = 8
PROJECTS_TARGET = 3
CERTS_TARGET = 2
APPLICATIONS_TARGET = 5
INTERVIEWS_TARGET = 2


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _int(v) -> int:
    try:
        return max(int(v or 0), 0)
    except (TypeError, ValueError):
        return 0


def label_of(item) -> str:
    """Skills / projects / certifications may be plain strings or small objects."""
    if isinstance(item, dict):
        for key in ("name", "title", "skill", "label"):
            if item.get(key):
                return str(item[key]).strip()
        return ""
    return str(item).strip() if item is not None else ""


def clean_list(value) -> list:
    if not isinstance(value, (list, tuple)):
        return []
    return [x for x in value if label_of(x)]


def normalize_cgpa(cgpa):
    """CGPA on a 10-point scale. Values that look like a percentage are converted."""
    if cgpa is None:
        return None
    try:
        v = float(cgpa)
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    if v > 100:
        return None
    if v > 10:
        v = v / 10
    return v


def band_for(score: float) -> tuple[str, str]:
    for minimum, key, label in BANDS:
        if score >= minimum:
            return key, label
    return BANDS[-1][1], BANDS[-1][2]


def _plural(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def compute_readiness(f: dict) -> dict:
    """
    f keys (all optional):
      cgpa, backlogs, skills, projects, certifications, resume_url, profile_completed,
      applications, interviews, offers   (counts)
      engagement_known  (bool, default True)
      market_skills     (Counter of skill -> number of drives asking for it, lowercase)
    """
    comps = {}
    strengths, recs = [], []

    # ---------------- Academics (25) ----------------
    cg = normalize_cgpa(f.get("cgpa"))
    backlogs = _int(f.get("backlogs"))
    cgpa_pts = 0.0 if cg is None else 20 * _clamp((cg - CGPA_FLOOR) / (CGPA_FULL - CGPA_FLOOR))
    backlog_pts = max(0.0, 5 - 2.5 * backlogs)
    academics = cgpa_pts + backlog_pts
    if cg is None:
        detail = "CGPA not added" + (", no backlogs" if backlogs == 0 else f", {_plural(backlogs, 'backlog')}")
    else:
        detail = f"CGPA {cg:.2f}, " + ("no backlogs" if backlogs == 0 else _plural(backlogs, "backlog"))
    comps["academics"] = (academics, detail)

    if cg is not None and cg >= 8:
        strengths.append(f"Strong CGPA of {cg:.2f}")
    if backlogs == 0 and cg is not None:
        strengths.append("No active backlogs")

    if backlogs > 0:
        recs.append({
            "component": "academics",
            "title": "Clear your backlogs",
            "detail": f"{_plural(backlogs, 'backlog')} pending. Many companies only allow students with no backlogs to sit for drives.",
            "potential": round(5 - backlog_pts, 1),
        })
    if cg is None:
        recs.append({
            "component": "academics",
            "title": "Add your CGPA to your profile",
            "detail": "Recruiters and eligibility checks rely on it.",
            "potential": 4.0,
        })
    elif cg < CGPA_FULL:
        recs.append({
            "component": "academics",
            "title": "Raise your CGPA where you can",
            "detail": f"CGPA is {cg:.2f}. Many companies set a cutoff around 6 to 7, and the score tops out at {CGPA_FULL}.",
            "potential": round(min(20 - cgpa_pts, 4), 1),  # capped: a CGPA moves slowly
        })

    # ---------------- Skills (20) ----------------
    skills = clean_list(f.get("skills"))
    market = f.get("market_skills") or None
    count_part = _clamp(len(skills) / SKILLS_TARGET)
    matched = []
    if market:
        have = {label_of(s).lower() for s in skills}
        matched = [s for s in skills if label_of(s).lower() in market]
        match = (len(matched) / len(skills)) if skills else 0.0
        skills_pts = 14 * count_part + 6 * match
        detail = f"{_plural(len(skills), 'skill')}, {len(matched)} in demand with recruiters"
    else:
        have = {label_of(s).lower() for s in skills}
        skills_pts = 20 * count_part
        detail = _plural(len(skills), "skill")
    comps["skills"] = (skills_pts, detail)

    if len(skills) >= 6:
        strengths.append(f"Good skill base ({len(skills)} skills listed)")
    if market and skills and len(matched) / len(skills) >= 0.5:
        strengths.append("Most of your skills match what open drives are asking for")

    if skills_pts < 20:
        wanted = []
        if market:
            wanted = [s for s, _ in market.most_common() if s not in have][:3]
        extra = f" Open drives often ask for: {', '.join(wanted)}." if wanted else ""
        need = max(SKILLS_TARGET - len(skills), 0)
        title = f"Add {_plural(need, 'more skill')}" if need else "Pick up in-demand skills"
        recs.append({
            "component": "skills",
            "title": title,
            "detail": ("List the tools and technologies you actually use." + extra).strip(),
            "potential": round(20 - skills_pts, 1),
            "suggested_skills": wanted,
        })

    # ---------------- Projects (15) ----------------
    projects = clean_list(f.get("projects"))
    proj_pts = 15 * _clamp(len(projects) / PROJECTS_TARGET)
    comps["projects"] = (proj_pts, _plural(len(projects), "project"))
    if len(projects) >= PROJECTS_TARGET:
        strengths.append(f"{len(projects)} projects on the profile")
    else:
        need = PROJECTS_TARGET - len(projects)
        recs.append({
            "component": "projects",
            "title": f"Add {_plural(need, 'project')}",
            "detail": "Recruiters look for projects that show you can build something end to end.",
            "potential": round(15 - proj_pts, 1),
        })

    # ---------------- Certifications (10) ----------------
    certs = clean_list(f.get("certifications"))
    cert_pts = 10 * _clamp(len(certs) / CERTS_TARGET)
    comps["certifications"] = (cert_pts, _plural(len(certs), "certification"))
    if len(certs) >= CERTS_TARGET:
        strengths.append(f"{len(certs)} certifications")
    else:
        need = CERTS_TARGET - len(certs)
        recs.append({
            "component": "certifications",
            "title": f"Earn {_plural(need, 'certification')}",
            "detail": "A relevant course or certificate backs up the skills you list.",
            "potential": round(10 - cert_pts, 1),
        })

    # ---------------- Profile and resume (10) ----------------
    has_resume = bool(f.get("resume_url"))
    done = bool(f.get("profile_completed"))
    profile_pts = (6 if has_resume else 0) + (4 if done else 0)
    bits = ["resume uploaded" if has_resume else "no resume", "profile complete" if done else "profile incomplete"]
    comps["profile"] = (profile_pts, ", ".join(bits))
    if has_resume and done:
        strengths.append("Resume uploaded and profile complete")
    if not has_resume:
        recs.append({
            "component": "profile",
            "title": "Upload your resume",
            "detail": "Recruiters can't shortlist you without it.",
            "potential": 6.0,
        })
    if not done:
        recs.append({
            "component": "profile",
            "title": "Complete your profile",
            "detail": "Fill in every section so you show up in recruiter searches.",
            "potential": 4.0,
        })

    # ---------------- Activity (20) ----------------
    engagement_known = f.get("engagement_known", True)
    apps = _int(f.get("applications"))
    interviews = _int(f.get("interviews"))
    offers = _int(f.get("offers"))
    if engagement_known:
        eng_pts = 20.0 if offers > 0 else 12 * _clamp(apps / APPLICATIONS_TARGET) + 8 * _clamp(interviews / INTERVIEWS_TARGET)
        parts = [_plural(apps, "application"), _plural(interviews, "interview")]
        if offers:
            parts.append(_plural(offers, "offer"))
        comps["engagement"] = (eng_pts, ", ".join(parts))
        if offers > 0:
            strengths.append(f"Holds {_plural(offers, 'offer')}")
        elif interviews >= INTERVIEWS_TARGET:
            strengths.append("Regularly reaching interviews")
        if offers == 0:
            if apps < APPLICATIONS_TARGET:
                recs.append({
                    "component": "engagement",
                    "title": "Apply to more drives",
                    "detail": f"You have applied to {apps}. Aim for at least {APPLICATIONS_TARGET} that match your profile.",
                    "potential": round(12 - 12 * _clamp(apps / APPLICATIONS_TARGET), 1),
                })
            if apps > 0 and interviews < INTERVIEWS_TARGET:
                recs.append({
                    "component": "engagement",
                    "title": "Turn applications into interviews",
                    "detail": "Few applications are reaching interviews. Review your resume and skills against the drive requirements.",
                    "potential": round(8 - 8 * _clamp(interviews / INTERVIEWS_TARGET), 1),
                })
    else:
        comps["engagement"] = (None, "Activity tracking not available")

    # ---------------- Total ----------------
    available = {k: v for k, v in comps.items() if v[0] is not None}
    earned = sum(v[0] for v in available.values())
    max_total = sum(WEIGHTS[k] for k in available)
    score = round(earned / max_total * 100) if max_total else 0
    band_key, band_label = band_for(score)

    components = []
    for key in WEIGHTS:
        pts, detail = comps[key]
        components.append({
            "key": key,
            "label": LABELS[key],
            "score": None if pts is None else round(pts, 1),
            "max": WEIGHTS[key],
            "available": pts is not None,
            "detail": detail,
        })

    recs = [r for r in recs if r["potential"] > 0]
    recs.sort(key=lambda r: r["potential"], reverse=True)
    recs = recs[:5]
    gain = sum(r["potential"] for r in recs[:3])
    potential_score = min(100, round((earned + gain) / max_total * 100)) if max_total else score

    return {
        "score": score,
        "band": band_key,
        "band_label": band_label,
        "components": components,
        "strengths": strengths[:5],
        "gaps": [r["title"] for r in recs],
        "recommendations": recs,
        "potential_score": max(potential_score, score),
        "has_offer": offers > 0,
        "engagement_known": bool(engagement_known),
        "market_data": bool(market),
    }


def demand_counter(drives_skill_lists) -> Counter | None:
    """Counts how many drives ask for each skill (lowercase). None when there's no data."""
    counter: Counter = Counter()
    for skills in drives_skill_lists:
        for s in skills:
            s = label_of(s).lower()
            if s:
                counter[s] += 1
    return counter or None