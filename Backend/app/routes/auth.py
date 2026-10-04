import hmac
import logging
import re
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.core.otp import generate_otp, hash_otp, send_otp_email
from app.models.schemas import (
    UserRegister,
    UserLogin,
    UserOut,
    Token,
    UserRole,
    UserNameUpdate,
    PasswordChange,
    AccountDeleteRequest,
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_OTP_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def user_to_out(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"],
    }


def login_response(user: dict) -> dict:
    """Same response shape as the password login, so the frontend treats both alike."""
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]}
    )
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_to_out(user),
        },
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    db = get_db()

    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    if payload.role == UserRole.student and not payload.branch:
        raise HTTPException(status_code=400, detail="branch is required for students")
    if payload.role == UserRole.recruiter and not payload.company_name:
        raise HTTPException(status_code=400, detail="company_name is required for recruiters")

    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": payload.role.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    if payload.role == UserRole.student:
        await db.students.insert_one({
            "user_id": user_id,
            "branch": payload.branch,
            "cgpa": None,
            "backlogs": 0,
            "skills": [],
            "certifications": [],
            "projects": [],
            "resume_url": None,
            "profile_completed": False,
        })
    elif payload.role == UserRole.recruiter:
        await db.recruiters.insert_one({
            "user_id": user_id,
            "company_name": payload.company_name,
            "company_details": None,
            "designation": None,
        })
    elif payload.role == UserRole.placement_officer:
        await db.placement_officers.insert_one({
            "user_id": user_id,
            "department": payload.department,
        })

    user_doc["_id"] = result.inserted_id
    return {
        "success": True,
        "message": "Registration successful",
        "data": user_to_out(user_doc),
    }


@router.post("/login", response_model=None)
async def login(payload: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": payload.email})

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return login_response(user)


# ---------------------------------------------------------------------------
# OTP (email code) login
# ---------------------------------------------------------------------------

class OtpRequest(BaseModel):
    email: EmailStr


class OtpVerify(BaseModel):
    email: EmailStr
    otp: str


def _aware(dt: datetime) -> datetime:
    # Mongo returns naive datetimes by default
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def find_user_by_email(db, email: str):
    # register stores the email as typed, so match case-insensitively
    return await db.users.find_one(
        {"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}}
    )


@router.post("/request-otp")
async def request_otp(payload: OtpRequest):
    db = get_db()
    email = payload.email.lower().strip()
    now = datetime.now(timezone.utc)
    generic = {
        "success": True,
        "message": "If that email is registered, a code has been sent.",
        "data": {},
    }

    # Within the cooldown, do nothing; the previous code is still valid.
    existing = await db.otps.find_one({"email": email})
    if existing and (now - _aware(existing["created_at"])).total_seconds() < RESEND_COOLDOWN_SECONDS:
        return generic

    user = await find_user_by_email(db, email)
    if not user or not user.get("is_active", True):
        return generic  # same response, so nobody can probe which emails exist

    otp = generate_otp()
    await db.otps.replace_one(
        {"email": email},
        {
            "email": email,
            "otp_hash": hash_otp(email, otp),
            "attempts": 0,
            "created_at": now,
            "expires_at": now + timedelta(minutes=settings.otp_expire_minutes),
        },
        upsert=True,
    )

    try:
        await run_in_threadpool(send_otp_email, email, otp)  # SMTP is blocking
    except Exception:
        # Shown in this terminal only. If emails don't arrive, look here.
        logger.exception("Failed to send OTP email")

    return generic


@router.post("/verify-otp")
async def verify_otp(payload: OtpVerify):
    db = get_db()
    email = payload.email.lower().strip()
    record = await db.otps.find_one({"email": email})

    if not record or _aware(record["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Code expired or invalid. Request a new one.")

    if record["attempts"] >= MAX_OTP_ATTEMPTS:
        await db.otps.delete_one({"email": email})
        raise HTTPException(status_code=400, detail="Too many attempts. Request a new code.")

    if not hmac.compare_digest(record["otp_hash"], hash_otp(email, payload.otp.strip())):
        await db.otps.update_one({"email": email}, {"$inc": {"attempts": 1}})
        raise HTTPException(status_code=400, detail="Incorrect code.")

    await db.otps.delete_one({"email": email})  # single use

    user = await find_user_by_email(db, email)
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Invalid request.")

    return login_response(user)


# ---------------------------------------------------------------------------

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "message": "Current user fetched",
        "data": user_to_out(current_user),
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # JWTs are stateless, so "logout" here just confirms the token is valid
    # and instructs the client to discard it. If we later need server-side
    # invalidation (e.g. forced logout), we'd add a token_blacklist collection
    # and check it inside get_current_user.
    return {
        "success": True,
        "message": "Logged out. Please delete the token on the client.",
        "data": {},
    }

@router.patch("/me")
async def update_my_name(
    payload: UserNameUpdate, current_user: dict = Depends(get_current_user)
):
    db = get_db()
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": {"name": payload.name}})
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return {"success": True, "message": "Name updated", "data": user_to_out(updated)}


@router.patch("/change-password")
async def change_password(
    payload: PasswordChange, current_user: dict = Depends(get_current_user)
):
    if not verify_password(payload.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    db = get_db()
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"password_hash": hash_password(payload.new_password)}},
    )
    return {"success": True, "message": "Password changed successfully", "data": {}}


@router.post("/delete-account")
async def delete_account(
    payload: AccountDeleteRequest, current_user: dict = Depends(get_current_user)
):
    if not verify_password(payload.password, current_user["password_hash"]):
        raise HTTPException(status_code=400, detail="Password is incorrect")

    db = get_db()
    user_id = current_user["_id"]
    role = current_user["role"]

    # Note: this only removes the user + their role-profile document.
    # Related applications/drives/interviews/offers/documents/notifications
    # are intentionally left in place — see the conversation note on
    # cascade-deletion before changing this.
    if role == "student":
        await db.students.delete_one({"user_id": str(user_id)})
    elif role == "recruiter":
        await db.recruiters.delete_one({"user_id": str(user_id)})
    elif role == "placement_officer":
        await db.placement_officers.delete_one({"user_id": str(user_id)})

    await db.users.delete_one({"_id": user_id})

    return {"success": True, "message": "Account deleted", "data": {}}