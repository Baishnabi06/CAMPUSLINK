"""
Pydantic models for request/response validation and MongoDB schema design
for CampusLink.

Placement Pipeline:
    Application
        ↓
    Technical Interview
        ↓
    HR Interview
        ↓
    Selected / Rejected

Each application contains a `rounds` array.

Round status:
    pending  -> round is available to be evaluated
    passed   -> recruiter passed the student
    failed   -> recruiter failed the student
    locked   -> previous round has not been passed yet
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    student = "student"
    recruiter = "recruiter"
    placement_officer = "placement_officer"


# ---------------------------------------------------------------------------
# users collection
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole

    branch: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# students collection
# ---------------------------------------------------------------------------

class StudentProfileCreate(BaseModel):
    user_id: str
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    backlogs: int = 0
    skills: list[str] = []
    certifications: list[str] = []
    projects: list[str] = []
    resume_url: Optional[str] = None
    profile_completed: bool = False


class StudentProfileUpdate(BaseModel):
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    backlogs: Optional[int] = None
    skills: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    projects: Optional[list[str]] = None
    resume_url: Optional[str] = None
    profile_completed: Optional[bool] = None


# ---------------------------------------------------------------------------
# recruiters collection
# ---------------------------------------------------------------------------

class RecruiterProfileCreate(BaseModel):
    user_id: str
    company_name: str
    company_details: Optional[str] = None
    designation: Optional[str] = None


class RecruiterProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    company_details: Optional[str] = None
    designation: Optional[str] = None


# ---------------------------------------------------------------------------
# placement_officers collection
# ---------------------------------------------------------------------------

class PlacementOfficerProfileCreate(BaseModel):
    user_id: str
    department: Optional[str] = None


# ---------------------------------------------------------------------------
# Drives
# ---------------------------------------------------------------------------

class DriveMode(str, Enum):
    online = "online"
    offline = "offline"
    hybrid = "hybrid"


class DriveStatus(str, Enum):
    open = "open"
    closed = "closed"
    completed = "completed"


class DriveCreate(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    required_branches: list[str] = []
    min_cgpa: float = 0
    max_backlogs: int = 0
    required_skills: list[str] = []
    required_certifications: list[str] = []
    # Ordered round names, e.g. ["Technical Interview", "HR Interview"].
    # Empty -> applications.py falls back to its default two rounds.
    selection_rounds: list[str] = []
    ctc: float
    openings: int = 1
    application_deadline: datetime
    drive_date: datetime
    location: Optional[str] = None
    mode: DriveMode = DriveMode.offline


class DriveUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    required_branches: Optional[list[str]] = None
    min_cgpa: Optional[float] = None
    max_backlogs: Optional[int] = None
    required_skills: Optional[list[str]] = None
    required_certifications: Optional[list[str]] = None
    selection_rounds: Optional[list[str]] = None
    ctc: Optional[float] = None
    openings: Optional[int] = None
    application_deadline: Optional[datetime] = None
    drive_date: Optional[datetime] = None
    location: Optional[str] = None
    mode: Optional[DriveMode] = None
    status: Optional[DriveStatus] = None


# ---------------------------------------------------------------------------
# Application Status
# ---------------------------------------------------------------------------

class ApplicationStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    rejected = "rejected"
    selected = "selected"


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


# ---------------------------------------------------------------------------
# Placement Pipeline / Application Rounds
#
# Every application contains (as stored by app/routes/applications.py):
#
# rounds: [
#     {
#         "round_number": 1,
#         "name": "Technical Interview",
#         "status": "pending",
#         "score": null,
#         "updated_at": null,
#         "feedback": null
#     },
#     {
#         "round_number": 2,
#         "name": "HR Interview",
#         "status": "locked",
#         "score": null,
#         "updated_at": null,
#         "feedback": null
#     }
# ]
# ---------------------------------------------------------------------------

class ApplicationRoundType(str, Enum):
    technical_interview = "technical_interview"
    hr_interview = "hr_interview"


class ApplicationRoundStatus(str, Enum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    locked = "locked"


class ApplicationRound(BaseModel):
    round_number: int
    name: str
    status: ApplicationRoundStatus
    score: Optional[float] = None
    feedback: Optional[str] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Recruiter evaluates a round
# ---------------------------------------------------------------------------

class RoundEvaluationStatus(str, Enum):
    """Only these two outcomes are valid when evaluating a round."""
    passed = "passed"
    failed = "failed"


class RoundStatusUpdate(BaseModel):
    """Body for PATCH /api/applications/{application_id}/round"""
    round_number: int = Field(ge=1)  # 1-based
    status: RoundEvaluationStatus
    score: float = Field(ge=0, le=100)
    feedback: Optional[str] = None


# Kept for backward compatibility with any other module that imports it.
class ApplicationRoundUpdate(BaseModel):
    status: ApplicationRoundStatus
    score: Optional[float] = Field(default=None, ge=0)
    feedback: Optional[str] = None


# ---------------------------------------------------------------------------
# Interviews
# ---------------------------------------------------------------------------

class InterviewMode(str, Enum):
    online = "online"
    offline = "offline"


class InterviewStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class InterviewCreate(BaseModel):
    application_id: str
    date: str
    start_time: str
    end_time: str
    mode: InterviewMode
    venue_or_link: str
    panel: list[str] = []
    force: bool = False

    # Technical Interview / HR Interview
    round: ApplicationRoundType = ApplicationRoundType.technical_interview


class InterviewUpdate(BaseModel):
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    mode: Optional[InterviewMode] = None
    venue_or_link: Optional[str] = None
    panel: Optional[list[str]] = None
    force: bool = False

    # Technical Interview / HR Interview
    round: Optional[ApplicationRoundType] = None


class InterviewStatusUpdate(BaseModel):
    status: InterviewStatus


# ---------------------------------------------------------------------------
# Offers
# ---------------------------------------------------------------------------

class OfferStatus(str, Enum):
    offer_generated = "offer_generated"
    offer_accepted = "offer_accepted"
    offer_rejected = "offer_rejected"
    offer_withdrawn = "offer_withdrawn"
    joining_pending = "joining_pending"
    joined = "joined"
    did_not_join = "did_not_join"


class OfferCreate(BaseModel):
    application_id: str
    ctc: float
    offer_date: str
    joining_date: str


class OfferResponse(BaseModel):
    response: str


class OfferStatusUpdate(BaseModel):
    status: OfferStatus


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class DocumentVerificationStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class DocumentCreate(BaseModel):
    document_type: str


class DocumentVerify(BaseModel):
    verification_status: DocumentVerificationStatus


# ---------------------------------------------------------------------------
# Account / Settings
# ---------------------------------------------------------------------------

class UserNameUpdate(BaseModel):
    name: str = Field(min_length=1)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class AccountDeleteRequest(BaseModel):
    password: str