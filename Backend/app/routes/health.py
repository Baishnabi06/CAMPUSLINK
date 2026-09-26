from fastapi import APIRouter
from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "CampusLink backend is running",
        "data": {"status": "ok"},
    }


@router.get("/health/db")
async def health_check_db():
    database = get_db()
    try:
        await database.command("ping")
        return {
            "success": True,
            "message": "MongoDB connection is healthy",
            "data": {"status": "connected"},
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"MongoDB connection failed: {str(e)}",
        }