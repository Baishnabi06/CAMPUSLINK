from fastapi import APIRouter, Depends

from app.database import get_db
from app.core.deps import require_role

router = APIRouter()


@router.get("/student/summary")
async def student_dashboard_summary(current_user: dict = Depends(require_role("student"))):
    db = get_db()
    student_id = str(current_user["_id"])

    student = await db.students.find_one({"user_id": student_id})
    profile_completed = bool(student and student.get("profile_completed"))

    available_drives = await db.drives.count_documents({"status": "open"})
    my_applications = await db.applications.count_documents({"student_id": student_id})
    upcoming_interviews = await db.interviews.count_documents(
        {"student_id": student_id, "status": "scheduled"}
    )
    my_offers = await db.offers.count_documents({"student_id": student_id})

    return {
        "success": True,
        "message": "Dashboard summary fetched",
        "data": {
            "profile_completed": profile_completed,
            "available_drives": available_drives,
            "my_applications": my_applications,
            "upcoming_interviews": upcoming_interviews,
            "my_offers": my_offers,
        },
    }


@router.get("/recruiter/summary")
async def recruiter_dashboard_summary(current_user: dict = Depends(require_role("recruiter"))):
    db = get_db()
    recruiter_id = str(current_user["_id"])

    drive_ids = [str(d["_id"]) async for d in db.drives.find({"recruiter_id": recruiter_id})]
    active_drives = await db.drives.count_documents({"recruiter_id": recruiter_id, "status": "open"})

    applications_count = await db.applications.count_documents({"drive_id": {"$in": drive_ids}})
    shortlisted_count = await db.applications.count_documents(
        {"drive_id": {"$in": drive_ids}, "status": "shortlisted"}
    )
    interviews_count = await db.interviews.count_documents({"recruiter_id": recruiter_id})
    offers_count = await db.offers.count_documents({"recruiter_id": recruiter_id})
    hired_count = await db.offers.count_documents(
        {"recruiter_id": recruiter_id, "status": {"$in": ["joining_pending", "joined"]}}
    )

    return {
        "success": True,
        "message": "Dashboard summary fetched",
        "data": {
            "active_drives": active_drives,
            "total_drives": len(drive_ids),
            "applications": applications_count,
            "shortlisted": shortlisted_count,
            "interviews": interviews_count,
            "offers": offers_count,
            "hired": hired_count,
        },
    }


@router.get("/officer/summary")
async def officer_dashboard_summary(current_user: dict = Depends(require_role("placement_officer"))):
    db = get_db()

    total_students = await db.students.count_documents({})
    placement_ready = await db.students.count_documents({"profile_completed": True})
    active_drives = await db.drives.count_documents({"status": "open"})
    total_applications = await db.applications.count_documents({})
    shortlisted = await db.applications.count_documents({"status": "shortlisted"})
    selected = await db.applications.count_documents({"status": "selected"})
    total_offers = await db.offers.count_documents({})
    placed = await db.offers.count_documents({"status": "joined"})
    pending_joining = await db.offers.count_documents({"status": "joining_pending"})

    return {
        "success": True,
        "message": "Dashboard summary fetched",
        "data": {
            "total_students": total_students,
            "placement_ready_students": placement_ready,
            "active_drives": active_drives,
            "total_applications": total_applications,
            "shortlisted": shortlisted,
            "selected_students": selected,
            "total_offers": total_offers,
            "placed_students": placed,
            "pending_joining": pending_joining,
        },
    }


@router.get("/officer/placement-stats")
async def officer_placement_analytics(current_user: dict = Depends(require_role("placement_officer"))):
    """
    Deterministic, database-driven placement analytics.
    NOT predictive — this is arithmetic over stored records, not a model.
    """
    db = get_db()

    total_students = await db.students.count_documents({})

    placed_student_ids = set()
    ctcs = []
    company_counts: dict[str, int] = {}

    async for offer in db.offers.find({"status": {"$in": ["joining_pending", "joined"]}}):
        placed_student_ids.add(offer["student_id"])
        ctcs.append(offer["ctc"])
        company_counts[offer["company_name"]] = company_counts.get(offer["company_name"], 0) + 1

    placement_percentage = (
        round(len(placed_student_ids) / total_students * 100, 2) if total_students else 0
    )
    average_package = round(sum(ctcs) / len(ctcs), 2) if ctcs else 0
    highest_package = max(ctcs) if ctcs else 0

    branch_counts: dict[str, int] = {}
    for student_id in placed_student_ids:
        student = await db.students.find_one({"user_id": student_id})
        branch = (student.get("branch") or "Unknown") if student else "Unknown"
        branch_counts[branch] = branch_counts.get(branch, 0) + 1

    total_applications = await db.applications.count_documents({})
    total_selected = await db.applications.count_documents({"status": "selected"})
    selection_rate = round(total_selected / total_applications * 100, 2) if total_applications else 0

    total_drives = await db.drives.count_documents({})
    applications_per_drive = round(total_applications / total_drives, 2) if total_drives else 0

    return {
        "success": True,
        "message": "Placement analytics fetched",
        "data": {
            "placement_count": len(placed_student_ids),
            "placement_percentage": placement_percentage,
            "average_package": average_package,
            "highest_package": highest_package,
            "branch_wise_placements": branch_counts,
            "company_wise_hiring": company_counts,
            "applications_per_drive": applications_per_drive,
            "selection_rate": selection_rate,
        },
    }