import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, get_db
from app.routes import (
    health,
    auth,
    demo,
    students,
    recruiters,
    drives,
    applications,
    interviews,
    offers,
    documents,
    notifications,
    analytics,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="CampusLink API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(recruiters.router, prefix="/api/recruiters", tags=["recruiters"])
app.include_router(drives.router, prefix="/api/drives", tags=["drives"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
app.include_router(offers.router, prefix="/api/offers", tags=["offers"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.on_event("startup")
async def on_startup():
    await connect_to_mongo()

    # Indexes for the OTP login codes. A failure here shouldn't stop the app.
    try:
        otps = get_db().otps
        await otps.create_index("expires_at", expireAfterSeconds=0)  # auto-delete expired codes
        await otps.create_index("email", unique=True)
    except Exception:
        logger.exception("Could not create OTP indexes")


@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Welcome to the CampusLink API",
        "data": {},
    }