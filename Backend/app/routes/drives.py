from datetime import datetime, timezone
from app.services.notifications import notify_all_students
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role
from app.models.schemas import DriveCreate, DriveUpdate

router = APIRouter()


def drive_out(drive: dict) -> dict:
    drive = dict(drive)
    drive["id"] = str(drive["_id"])
    del drive["_id"]
    return drive


async def get_owned_drive_or_404(db, drive_id: str, recruiter_id: str):
    try:
        oid = ObjectId(drive_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid drive id")

    drive = await db.drives.find_one({"_id": oid})
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")
    if drive["recruiter_id"] != recruiter_id:
        raise HTTPException(status_code=403, detail="You do not own this drive")
    return drive


@router.post("", status_code=201)
async def create_drive(
    payload: DriveCreate, current_user: dict = Depends(require_role("recruiter"))
):
    db = get_db()
    doc = payload.model_dump()
    doc["mode"] = doc["mode"].value if hasattr(doc["mode"], "value") else doc["mode"]
    doc["recruiter_id"] = str(current_user["_id"])
    doc["status"] = "open"
    doc["created_at"] = datetime.now(timezone.utc)

    result = await db.drives.insert_one(doc)
    doc["_id"] = result.inserted_id
    await notify_all_students(
        db, "New Placement Drive", f"{doc['company_name']} has posted a new drive: {doc['job_title']}"
    )
    return {"success": True, "message": "Drive created", "data": drive_out(doc)}


@router.get("/mine")
async def list_my_drives(current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    cursor = db.drives.find({"recruiter_id": str(current_user["_id"])}).sort("created_at", -1)
    drives = [drive_out(d) async for d in cursor]
    return {"success": True, "message": "Drives fetched", "data": drives}


@router.get("/open")
async def list_open_drives(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    cursor = db.drives.find({"status": "open"}).sort("created_at", -1)
    drives = [drive_out(d) async for d in cursor]
    return {"success": True, "message": "Open drives fetched", "data": drives}


@router.get("/open/{drive_id}")
async def get_open_drive(drive_id: str, current_user: dict = Depends(require_role("student"))):
    db = get_db()
    try:
        oid = ObjectId(drive_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid drive id")
    drive = await db.drives.find_one({"_id": oid, "status": "open"})
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found or not open")
    return {"success": True, "message": "Drive fetched", "data": drive_out(drive)}


@router.get("/{drive_id}")
async def get_drive(drive_id: str, current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    drive = await get_owned_drive_or_404(db, drive_id, str(current_user["_id"]))
    return {"success": True, "message": "Drive fetched", "data": drive_out(drive)}


@router.put("/{drive_id}")
async def update_drive(
    drive_id: str,
    payload: DriveUpdate,
    current_user: dict = Depends(require_role("recruiter")),
):
    db = get_db()
    await get_owned_drive_or_404(db, drive_id, str(current_user["_id"]))

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "mode" in update_data and hasattr(update_data["mode"], "value"):
        update_data["mode"] = update_data["mode"].value
    if "status" in update_data and hasattr(update_data["status"], "value"):
        update_data["status"] = update_data["status"].value

    if update_data:
        await db.drives.update_one({"_id": ObjectId(drive_id)}, {"$set": update_data})

    updated = await db.drives.find_one({"_id": ObjectId(drive_id)})
    return {"success": True, "message": "Drive updated", "data": drive_out(updated)}


@router.delete("/{drive_id}")
async def delete_drive(drive_id: str, current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    await get_owned_drive_or_404(db, drive_id, str(current_user["_id"]))
    await db.drives.delete_one({"_id": ObjectId(drive_id)})
    return {"success": True, "message": "Drive deleted", "data": {}}