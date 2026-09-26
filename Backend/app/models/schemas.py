"""
Pydantic models for request/response validation, and the reference schema
design for every MongoDB collection in CampusLink.

Collections implemented with real logic in Stage 2: users, students,
recruiters, placement_officers.

Collections documented here as a schema reference, to be implemented in
later stages: drives (Stage 4), applications (Stage 5), interviews
(Stage 6), offers/documents/notifications (Stage 7).
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
# {
#   _id, name, email, password_hash, role, is_active, created_at
# }
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole

    # Optional role-specific fields collected at registration time
    branch: Optional[str] = None          # required for students
    company_name: Optional[str] = None    # required for recruiters
    department: Optional[str] = None      # required for placement_officers


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
# {
#   _id, user_id, branch, cgpa, backlogs, skills: [], certifications: [],
#   projects: [], resume_url, profile_completed: bool
# }
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
# ---------------------------------------------------------------------------
# recruiters collection
# {
#   _id, user_id, company_name, company_details, designation
# }
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
    ctc: Optional[float] = None
    openings: Optional[int] = None
    application_deadline: Optional[datetime] = None
    drive_date: Optional[datetime] = None
    location: Optional[str] = None
    mode: Optional[DriveMode] = None
    status: Optional[DriveStatus] = None
# ---------------------------------------------------------------------------
# placement_officers collection
# {
#   _id, user_id, department
# }
# ---------------------------------------------------------------------------

class PlacementOfficerProfileCreate(BaseModel):
    user_id: str
    department: Optional[str] = None



class ApplicationStatus(str, Enum):
    applied = "applied"
    shortlisted = "shortlisted"
    rejected = "rejected"
    selected = "selected"


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus




class InterviewMode(str, Enum):
    online = "online"
    offline = "offline"


class InterviewStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class InterviewCreate(BaseModel):
    application_id: str
    date: str          # "YYYY-MM-DD"
    start_time: str     # "HH:MM" (24-hour)
    end_time: str
    mode: InterviewMode
    venue_or_link: str
    panel: list[str] = []
    force: bool = False


class InterviewUpdate(BaseModel):
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    mode: Optional[InterviewMode] = None
    venue_or_link: Optional[str] = None
    panel: Optional[list[str]] = None
    force: bool = False


class InterviewStatusUpdate(BaseModel):
    status: InterviewStatus




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
    offer_date: str     # "YYYY-MM-DD"
    joining_date: str    # "YYYY-MM-DD"


class OfferResponse(BaseModel):
    response: str  # "accept" or "reject"


class OfferStatusUpdate(BaseModel):
    status: OfferStatus




class DocumentVerificationStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class DocumentCreate(BaseModel):
    document_type: str


class DocumentVerify(BaseModel):
    verification_status: DocumentVerificationStatus