from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    await client.admin.command("ping")
    await create_indexes()


async def create_indexes():
    await db.users.create_index("email", unique=True)
    await db.students.create_index("user_id", unique=True)
    await db.recruiters.create_index("user_id", unique=True)
    await db.placement_officers.create_index("user_id", unique=True)


async def close_mongo_connection():
    global client
    if client:
        client.close()


def get_db():
    return db