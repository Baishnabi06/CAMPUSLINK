from datetime import datetime, timezone


async def create_notification(db, user_id: str, title: str, message: str):
    await db.notifications.insert_one(
        {
            "user_id": user_id,
            "title": title,
            "message": message,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        }
    )


async def notify_all_students(db, title: str, message: str):
    cursor = db.users.find({"role": "student"})
    async for user in cursor:
        await create_notification(db, str(user["_id"]), title, message)


async def notify_all_officers(db, title: str, message: str):
    cursor = db.users.find({"role": "placement_officer"})
    async for user in cursor:
        await create_notification(db, str(user["_id"]), title, message)