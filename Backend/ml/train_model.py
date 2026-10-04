"""
Trains the CampusLink placement-probability model and saves it.

Run (from the Backend folder, venv active):
    pip install scikit-learn pandas joblib
    python ml/generate_dataset.py     # only if you have no real data yet
    python ml/train_model.py
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).parent
DATA = BASE / "data" / "placement_data.csv"
MODEL_PATH = BASE / "models" / "placement_model.joblib"

FEATURES = [
    "cgpa",
    "active_backlogs",
    "skills_count",
    "projects_count",
    "certifications_count",
    "internships_count",
    "has_resume",
    "applications_count",
]
TARGET = "placed"


def main():
    df = pd.read_csv(DATA).dropna(subset=FEATURES + [TARGET])
    X, y = df[FEATURES], df[TARGET]
    print(f"Rows: {len(df)} | placed rate: {y.mean():.1%}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logreg = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    forest = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)

    for name, model in [("LogisticRegression", logreg), ("RandomForest", forest)]:
        cv = cross_val_score(model, X_train, y_train, cv=5, scoring="roc_auc")
        print(f"{name}: 5-fold CV AUC = {cv.mean():.3f} (+/- {cv.std():.3f})")

    # We ship logistic regression: nearly as accurate here, and its weights let
    # us explain WHY a student got their probability.
    logreg.fit(X_train, y_train)
    proba = logreg.predict_proba(X_test)[:, 1]
    print(f"\nHold-out test AUC: {roc_auc_score(y_test, proba):.3f}")
    print(classification_report(y_test, logreg.predict(X_test)))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": logreg, "features": FEATURES}, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
