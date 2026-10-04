import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.database import get_db
from app.core.deps import require_role


router = APIRouter()


INTERNSHIP_DIR = "uploads/internships"
os.makedirs(INTERNSHIP_DIR, exist_ok=True)


ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


def internship_out(internship: dict) -> dict:
    internship = dict(internship)
    internship["id"] = str(internship["_id"])
    del internship["_id"]
    return internship


@router.get("")
async def get_my_internships(
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()
    user_id = str(current_user["_id"])

    internships = []

    cursor = db.internships.find(
        {"student_id": user_id}
    ).sort("created_at", -1)

    async for internship in cursor:
        internships.append(internship_out(internship))

    return {
        "success": True,
        "message": "Internships fetched",
        "data": internships,
    }


@router.post("")
async def add_internship(
    company_name: str = Form(...),
    role: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role("student")),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, JPEG and PNG files are accepted",
        )

    db = get_db()
    user_id = str(current_user["_id"])

    extension = os.path.splitext(file.filename or "")[1].lower()

    if not extension:
        extension = ".pdf"

    filename = f"{user_id}_{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(INTERNSHIP_DIR, filename)

    content = await file.read()

    with open(filepath, "wb") as f:
        f.write(content)

    certificate_url = f"/uploads/internships/{filename}"

    internship = {
        "student_id": user_id,
        "company_name": company_name,
        "role": role,
        "start_date": start_date,
        "end_date": end_date,
        "description": description,
        "certificate_url": certificate_url,
        "certificate_filename": file.filename,
        "created_at": datetime.utcnow(),
    }

    result = await db.internships.insert_one(internship)

    internship["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Internship added",
        "data": internship_out(internship),
    }


@router.delete("/{internship_id}")
async def delete_internship(
    internship_id: str,
    current_user: dict = Depends(require_role("student")),
):
    from bson import ObjectId

    db = get_db()
    user_id = str(current_user["_id"])

    try:
        object_id = ObjectId(internship_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid internship ID",
        )

    internship = await db.internships.find_one(
        {
            "_id": object_id,
            "student_id": user_id,
        }
    )

    if not internship:
        raise HTTPException(
            status_code=404,
            detail="Internship not found",
        )

    certificate_url = internship.get("certificate_url")

    if certificate_url:
        filepath = certificate_url.lstrip("/").replace("/", os.sep)

        if os.path.exists(filepath):
            os.remove(filepath)

    await db.internships.delete_one(
        {
            "_id": object_id,
            "student_id": user_id,
        }
    )

    return {
        "success": True,
        "message": "Internship deleted",
    }