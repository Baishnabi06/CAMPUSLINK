from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends

from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.schemas import UserRegister, UserLogin, UserOut, Token, UserRole

router = APIRouter()


def user_to_out(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"],
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