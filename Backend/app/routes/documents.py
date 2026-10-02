from datetime import datetime, timezone
from app.services.notifications import create_notification
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from urllib.parse import quote

from app.database import get_db
from app.core.deps import require_role, get_current_user
from app.models.schemas import DocumentCreate, DocumentVerify

router = APIRouter()


def document_out(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.post("", status_code=201)
async def submit_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role("student")),
):
    db = get_db()

    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}

    filename = file.filename or ""
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: PDF, JPG, JPEG, PNG, DOC, DOCX",
        )

    file_content = await file.read()

    max_file_size = 10 * 1024 * 1024  # 10 MB

    if len(file_content) > max_file_size:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10 MB",
        )

    document = {
        "student_id": str(current_user["_id"]),
        "document_type": document_type,
        "file_name": filename,
        "file_content": file_content,
        "content_type": file.content_type,
        "submission_status": "submitted",
        "verification_status": "pending",
        "submitted_date": datetime.now(timezone.utc),
        "verified_date": None,
    }

    result = await db.documents.insert_one(document)
    document["_id"] = result.inserted_id

    # Do not return the binary file content in the API response
    response_document = document_out(document)
    response_document.pop("file_content", None)

    return {
        "success": True,
        "message": "Document submitted",
        "data": response_document,
    }


@router.get("/mine")
async def list_my_documents(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    cursor = db.documents.find({"student_id": str(current_user["_id"])}).sort("submitted_date", -1)
    docs = [document_out(d) async for d in cursor]
    return {"success": True, "message": "Documents fetched", "data": docs}


@router.get("/all")
async def list_all_documents(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("placement_officer", "recruiter"):
        raise HTTPException(status_code=403, detail="Not authorized")

    db = get_db()
    cursor = db.documents.find({}).sort("submitted_date", -1)
    results = []
    async for doc in cursor:
        user_doc = await db.users.find_one({"_id": ObjectId(doc["student_id"])})
        out = document_out(doc)
        out.pop("file_content", None)
        out["student_name"] = user_doc["name"] if user_doc else "Unknown"
        results.append(out)
    return {"success": True, "message": "All documents fetched", "data": results}


@router.get("/{document_id}/file")
async def get_document_file(
    document_id: str,
    current_user: dict = Depends(require_role("recruiter", "placement_officer")),
):
    db = get_db()
    try:
        oid = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document id")

    document = await db.documents.find_one({"_id": oid})
    if not document or "file_content" not in document:
        raise HTTPException(status_code=404, detail="Document file not found")

    filename = (document.get("file_name") or "document").replace("\\", "/").split("/")[-1]
    content_type = document.get("content_type") or "application/octet-stream"
    disposition = "inline" if content_type in {
        "application/pdf",
        "image/jpeg",
        "image/png",
    } else "attachment"

    return Response(
        content=document["file_content"],
        media_type=content_type,
        headers={
            "Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(filename, safe='')}",
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.patch("/{document_id}/verify")
async def verify_document(
    document_id: str,
    payload: DocumentVerify,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "placement_officer":
        raise HTTPException(status_code=403, detail="Only the placement officer can verify documents")

    db = get_db()
    try:
        oid = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document id")

    doc = await db.documents.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.documents.update_one(
        {"_id": oid},
        {
            "$set": {
                "verification_status": payload.verification_status.value,
                "verified_date": datetime.now(timezone.utc),
            }
        },
    )
    updated = await db.documents.find_one({"_id": oid})
    await create_notification(
        db,
        doc["student_id"],
        "Document Verification Update",
        f"Your document '{doc['document_type']}' has been marked '{payload.verification_status.value}'",
    )
    return {"success": True, "message": "Document verification updated", "data": document_out(updated)}