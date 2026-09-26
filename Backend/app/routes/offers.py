from datetime import datetime, timezone
from app.services.notifications import create_notification
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.core.deps import require_role, get_current_user
from app.models.schemas import OfferCreate, OfferResponse, OfferStatusUpdate

router = APIRouter()


def offer_out(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.post("", status_code=201)
async def create_offer(payload: OfferCreate, current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    try:
        app_oid = ObjectId(payload.application_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid application id")

    application = await db.applications.find_one({"_id": app_oid})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    drive = await db.drives.find_one({"_id": ObjectId(application["drive_id"])})
    if not drive or drive["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own the drive for this application")

    existing = await db.offers.find_one({"application_id": payload.application_id})
    if existing:
        raise HTTPException(status_code=400, detail="An offer already exists for this application")

    offer = {
        "student_id": application["student_id"],
        "recruiter_id": str(current_user["_id"]),
        "application_id": payload.application_id,
        "drive_id": application["drive_id"],
        "company_name": drive["company_name"],
        "job_title": drive["job_title"],
        "ctc": payload.ctc,
        "offer_date": payload.offer_date,
        "joining_date": payload.joining_date,
        "status": "offer_generated",
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.offers.insert_one(offer)
    offer["_id"] = result.inserted_id

    await db.applications.update_one({"_id": app_oid}, {"$set": {"status": "selected"}})
    await create_notification(
        db,
        application["student_id"],
        "Offer Generated",
        f"You have received an offer for {drive['job_title']} at {drive['company_name']} "
        f"(CTC {payload.ctc} LPA)",
    )
    return {"success": True, "message": "Offer created", "data": offer_out(offer)}


@router.get("/mine")
async def list_my_offers(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    cursor = db.offers.find({"student_id": str(current_user["_id"])}).sort("created_at", -1)
    offers = [offer_out(doc) async for doc in cursor]
    return {"success": True, "message": "Offers fetched", "data": offers}


@router.patch("/{offer_id}/respond")
async def respond_to_offer(
    offer_id: str, payload: OfferResponse, current_user: dict = Depends(require_role("student"))
):
    db = get_db()
    try:
        oid = ObjectId(offer_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid offer id")

    offer = await db.offers.find_one({"_id": oid})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer["student_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="This is not your offer")
    if offer["status"] != "offer_generated":
        raise HTTPException(status_code=400, detail="This offer is not awaiting a response")

    if payload.response not in ("accept", "reject"):
        raise HTTPException(status_code=400, detail="response must be 'accept' or 'reject'")

    new_status = "joining_pending" if payload.response == "accept" else "offer_rejected"

    await db.offers.update_one({"_id": oid}, {"$set": {"status": new_status}})
    updated = await db.offers.find_one({"_id": oid})
    return {"success": True, "message": "Response recorded", "data": offer_out(updated)}


@router.get("/recruiter/mine")
async def list_offers_i_created(current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    cursor = db.offers.find({"recruiter_id": str(current_user["_id"])}).sort("created_at", -1)
    results = []
    async for doc in cursor:
        user_doc = await db.users.find_one({"_id": ObjectId(doc["student_id"])})
        out = offer_out(doc)
        out["student_name"] = user_doc["name"] if user_doc else "Unknown"
        results.append(out)
    return {"success": True, "message": "Offers fetched", "data": results}


@router.patch("/{offer_id}/status")
async def update_offer_status(
    offer_id: str,
    payload: OfferStatusUpdate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in ("recruiter", "placement_officer"):
        raise HTTPException(status_code=403, detail="Not authorized")

    db = get_db()
    try:
        oid = ObjectId(offer_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid offer id")

    offer = await db.offers.find_one({"_id": oid})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if current_user["role"] == "recruiter" and offer["recruiter_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own this offer")

    await db.offers.update_one({"_id": oid}, {"$set": {"status": payload.status.value}})
    updated = await db.offers.find_one({"_id": oid})
    await create_notification(
        db,
        offer["student_id"],
        "Offer Update",
        f"Your offer status for {offer['job_title']} at {offer['company_name']} is now '{payload.status.value}'",
    )
    return {"success": True, "message": "Offer status updated", "data": offer_out(updated)}


@router.get("/all")
async def list_all_offers(current_user: dict = Depends(require_role("placement_officer"))):
    db = get_db()
    cursor = db.offers.find({}).sort("created_at", -1)
    results = []
    async for doc in cursor:
        user_doc = await db.users.find_one({"_id": ObjectId(doc["student_id"])})
        out = offer_out(doc)
        out["student_name"] = user_doc["name"] if user_doc else "Unknown"
        results.append(out)
    return {"success": True, "message": "All offers fetched", "data": results}