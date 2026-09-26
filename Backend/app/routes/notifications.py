from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import get_current_user

router = APIRouter()


def notification_out(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/mine")
async def list_my_notifications(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.notifications.find({"user_id": str(current_user["_id"])}).sort("created_at", -1)
    notifications = [notification_out(doc) async for doc in cursor]
    return {"success": True, "message": "Notifications fetched", "data": notifications}


@router.get("/unread-count")
async def unread_count(current_user: dict = Depends(get_current_user)):
    db = get_db()
    count = await db.notifications.count_documents(
        {"user_id": str(current_user["_id"]), "is_read": False}
    )
    return {"success": True, "message": "Unread count fetched", "data": {"count": count}}


@router.patch("/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(notification_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid notification id")

    notification = await db.notifications.find_one({"_id": oid})
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="This is not your notification")

    await db.notifications.update_one({"_id": oid}, {"$set": {"is_read": True}})
    updated = await db.notifications.find_one({"_id": oid})
    return {"success": True, "message": "Marked as read", "data": notification_out(updated)}


@router.patch("/read-all")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    db = get_db()
    await db.notifications.update_many(
        {"user_id": str(current_user["_id"]), "is_read": False}, {"$set": {"is_read": True}}
    )
    return {"success": True, "message": "All notifications marked as read", "data": {}}