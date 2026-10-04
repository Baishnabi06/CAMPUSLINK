"""
Generates a SYNTHETIC placement dataset for CampusLink (demo / training practice).

IMPORTANT: this data is artificial. It is built from a hand-written rule plus
random noise, so a model trained on it only learns that rule. Replace
data/placement_data.csv with real, anonymised past-placement records from your
placement cell as soon as you have them (same column names), then re-run
train_model.py.

Run:  python generate_dataset.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

N_ROWS = 1200
SEED = 42
OUT = Path(__file__).parent / "data" / "placement_data.csv"


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def main():
    rng = np.random.default_rng(SEED)

    cgpa = np.clip(rng.normal(7.4, 1.0, N_ROWS), 5.0, 10.0).round(2)
    backlogs = rng.choice([0, 1, 2, 3, 4], N_ROWS, p=[0.72, 0.15, 0.08, 0.03, 0.02])
    skills = np.clip(rng.poisson(5, N_ROWS), 0, 15)
    projects = np.clip(rng.poisson(2, N_ROWS), 0, 8)
    certs = np.clip(rng.poisson(1.5, N_ROWS), 0, 6)
    internships = rng.choice([0, 1, 2, 3], N_ROWS, p=[0.55, 0.30, 0.12, 0.03])
    has_resume = rng.choice([0, 1], N_ROWS, p=[0.25, 0.75])
    applications = np.clip(rng.poisson(4, N_ROWS), 0, 20)

    # Hidden "true" rule used only to create labels (demo purposes).
    logit = (
        -9.0
        + 0.85 * cgpa
        - 0.9 * backlogs
        + 0.18 * skills
        + 0.30 * projects
        + 0.20 * certs
        + 0.55 * internships
        + 0.70 * has_resume
        + 0.08 * applications
        + rng.normal(0, 0.8, N_ROWS)  # real life is noisy
    )
    placed = (rng.random(N_ROWS) < sigmoid(logit)).astype(int)

    df = pd.DataFrame({
        "cgpa": cgpa,
        "active_backlogs": backlogs,
        "skills_count": skills,
        "projects_count": projects,
        "certifications_count": certs,
        "internships_count": internships,
        "has_resume": has_resume,
        "applications_count": applications,
        "placed": placed,
    })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df)} rows to {OUT}")
    print(f"Placed rate: {df['placed'].mean():.1%}")


if __name__ == "__main__":
    main()
