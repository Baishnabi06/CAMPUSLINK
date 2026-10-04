import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.database import get_db
from app.core.deps import require_role


router = APIRouter()


CERTIFICATION_DIR = "uploads/certifications"
os.makedirs(CERTIFICATION_DIR, exist_ok=True)


ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


def certification_out(certification: dict) -> dict:
    certification = dict(certification)
    certification["id"] = str(certification["_id"])
    del certification["_id"]
    return certification


@router.get("")
async def get_my_certifications(
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()
    user_id = str(current_user["_id"])

    certifications = []

    cursor = db.certifications.find(
        {"student_id": user_id}
    ).sort("created_at", -1)

    async for certification in cursor:
        certifications.append(certification_out(certification))

    return {
        "success": True,
        "message": "Certifications fetched",
        "data": certifications,
    }


@router.post("")
async def add_certification(
    name: str = Form(...),
    issuing_organization: str = Form(...),
    issue_date: str = Form(...),
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
    filepath = os.path.join(CERTIFICATION_DIR, filename)

    content = await file.read()

    with open(filepath, "wb") as f:
        f.write(content)

    certificate_url = f"/uploads/certifications/{filename}"

    certification = {
        "student_id": user_id,
        "name": name,
        "issuing_organization": issuing_organization,
        "issue_date": issue_date,
        "certificate_url": certificate_url,
        "certificate_filename": file.filename,
        "created_at": datetime.utcnow(),
    }

    result = await db.certifications.insert_one(certification)

    certification["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Certification added",
        "data": certification_out(certification),
    }


@router.delete("/{certification_id}")
async def delete_certification(
    certification_id: str,
    current_user: dict = Depends(require_role("student")),
):
    from bson import ObjectId

    db = get_db()
    user_id = str(current_user["_id"])

    try:
        object_id = ObjectId(certification_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid certification ID",
        )

    certification = await db.certifications.find_one(
        {
            "_id": object_id,
            "student_id": user_id,
        }
    )

    if not certification:
        raise HTTPException(
            status_code=404,
            detail="Certification not found",
        )

    certificate_url = certification.get("certificate_url")

    if certificate_url:
        filepath = certificate_url.lstrip("/").replace("/", os.sep)

        if os.path.exists(filepath):
            os.remove(filepath)

    await db.certifications.delete_one(
        {
            "_id": object_id,
            "student_id": user_id,
        }
    )

    return {
        "success": True,
        "message": "Certification deleted",
    }