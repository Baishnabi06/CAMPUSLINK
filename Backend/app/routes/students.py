import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import StudentProfileUpdate

router = APIRouter()

RESUME_DIR = "uploads/resumes"
os.makedirs(RESUME_DIR, exist_ok=True)


def student_out(student: dict) -> dict:
    student = dict(student)
    student["id"] = str(student["_id"])
    del student["_id"]
    return student


@router.get("/me")
async def get_my_student_profile(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    student = await db.students.find_one({"user_id": str(current_user["_id"])})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return {"success": True, "message": "Student profile fetched", "data": student_out(student)}


@router.put("/me")
async def update_my_student_profile(
    payload: StudentProfileUpdate,
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()
    user_id = str(current_user["_id"])

    existing = await db.students.find_one({"user_id": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Student profile not found")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    merged = {**existing, **update_data}
    update_data["profile_completed"] = bool(
        merged.get("branch") and merged.get("cgpa") is not None and merged.get("skills")
    )

    await db.students.update_one({"user_id": user_id}, {"$set": update_data})
    updated = await db.students.find_one({"user_id": user_id})
    return {"success": True, "message": "Profile updated", "data": student_out(updated)}


@router.post("/me/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role("student")),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes are accepted")

    db = get_db()
    user_id = str(current_user["_id"])
    filename = f"{user_id}_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(RESUME_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    resume_url = f"/uploads/resumes/{filename}"
    await db.students.update_one({"user_id": user_id}, {"$set": {"resume_url": resume_url}})

    return {"success": True, "message": "Resume uploaded", "data": {"resume_url": resume_url}}