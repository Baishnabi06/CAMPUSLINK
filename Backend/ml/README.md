# CampusLink – own AI model (no paid API)

## Where the files go
```
Backend/
  ml/
    generate_dataset.py
    train_model.py
    data/placement_data.csv
    models/                      <- placement_model.joblib appears here after training
  app/services/ai/
    prediction_service.py        <- replaces your existing file (or merge the function in)
    feedback_service.py          <- new
```

## Steps (run from the Backend folder, venv active)
```
pip install scikit-learn pandas joblib
python ml/train_model.py
```
Add `scikit-learn`, `pandas`, `joblib` to requirements.txt.
Train on your own machine so the saved model matches your scikit-learn version.
Restart uvicorn afterwards.

## Using it in readiness.py (replace the Anthropic call)
```python
from app.services.ai.prediction_service import predict_placement, ModelNotTrainedError
from app.services.ai.feedback_service import build_feedback

profile = {
    "cgpa": student.cgpa,
    "active_backlogs": student.active_backlogs,
    "skills_count": len(student.skills or []),
    "projects_count": len(student.projects or []),
    "certifications_count": len(student.certifications or []),
    "internships_count": 0,          # use your real field if you have one
    "has_resume": bool(student.resume_path),
    "applications_count": applications_count,
}

try:
    prediction = predict_placement(profile)
except ModelNotTrainedError:
    prediction = None

return {"feedback": build_feedback(profile, prediction), "prediction": prediction}
```
Adjust the `student.*` field names to match your model.

## Important: the dataset is synthetic
`data/placement_data.csv` is generated from a hand-written rule plus noise.
The model only learns that rule, so its accuracy says nothing about real placements.
State this clearly in your report/viva. For real results, replace the CSV with
anonymised past placement records from your placement cell (same column names,
`placed` = 1 or 0) and re-run `python ml/train_model.py`.
