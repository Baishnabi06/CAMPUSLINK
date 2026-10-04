"""
Placement-probability prediction using the model trained by ml/train_model.py.

Usage (from a route):
    from app.services.ai.prediction_service import predict_placement

    result = predict_placement({
        "cgpa": 8.96, "active_backlogs": 0, "skills_count": 9,
        "projects_count": 4, "certifications_count": 2,
        "internships_count": 0, "has_resume": False, "applications_count": 0,
    })
    # -> {"probability": 0.87, "percent": 87, "band": "High",
    #     "helping": [...], "hurting": [...]}
"""
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

# .../Backend/app/services/ai/prediction_service.py -> .../Backend
BACKEND_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BACKEND_DIR / "ml" / "models" / "placement_model.joblib"

LABELS = {
    "cgpa": "CGPA",
    "active_backlogs": "Active backlogs",
    "skills_count": "Number of skills",
    "projects_count": "Projects",
    "certifications_count": "Certifications",
    "internships_count": "Internships",
    "has_resume": "Resume uploaded",
    "applications_count": "Drive applications",
}


class ModelNotTrainedError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _load():
    if not MODEL_PATH.exists():
        raise ModelNotTrainedError(
            f"Model file not found at {MODEL_PATH}. Run: python ml/train_model.py"
        )
    bundle = joblib.load(MODEL_PATH)
    return bundle["model"], bundle["features"]


def _band(p: float) -> str:
    if p >= 0.70:
        return "High"
    if p >= 0.40:
        return "Moderate"
    return "Low"


def predict_placement(profile: dict) -> dict:
    """Return placement probability plus the factors helping/hurting the student."""
    model, features = _load()
    row = pd.DataFrame([{f: float(profile.get(f, 0) or 0) for f in features}])

    probability = float(model.predict_proba(row)[0, 1])

    # Explain: coefficient x standardised value = push up (+) or down (-)
    scaler = model.named_steps["standardscaler"]
    clf = model.named_steps["logisticregression"]
    scaled = scaler.transform(row)[0]
    contributions = {f: float(c * v) for f, c, v in zip(features, clf.coef_[0], scaled)}

    ranked = sorted(contributions.items(), key=lambda kv: kv[1])
    hurting = [LABELS[f] for f, c in ranked if c < -0.15][:3]
    helping = [LABELS[f] for f, c in reversed(ranked) if c > 0.15][:3]

    return {
        "probability": round(probability, 3),
        "percent": min(99, max(1, round(probability * 100))),
        "band": _band(probability),
        "helping": helping,
        "hurting": hurting,
        "contributions": {LABELS[f]: round(c, 3) for f, c in contributions.items()},
    }
