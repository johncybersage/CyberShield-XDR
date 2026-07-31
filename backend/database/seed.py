import asyncio
import uuid

from backend.auth.security import hash_password
from backend.database.session import AsyncSessionLocal, init_db
from backend.models.asset import Asset
from backend.models.user import User, UserRole


async def seed_database():
    print("Initializing tables...")
    await init_db()

    print("Seeding initial data...")
    async_session = AsyncSessionLocal()
    async with async_session as session:
        # Check if admin user already exists
        # In a real app we would query the database, for simplicity we assume empty DB if seed is called
        
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@cybershield.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=hash_password("Str0ng@Admin!123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        soc_user = User(
            id=uuid.uuid4(),
            email="soc@cybershield.com",
            username="soc_analyst",
            full_name="SOC Analyst",
            hashed_password=hash_password("Str0ng@Soc!123"),
            role=UserRole.SOC_ANALYST,
            is_active=True
        )

        sample_asset = Asset(
            id=uuid.uuid4(),
            ip_address="192.168.1.100",
            hostname="web-server-prod",
            mac_address="00:1B:44:11:3A:B7",
            os_name="Ubuntu",
            os_version="22.04",
        )

        session.add_all([admin_user, soc_user, sample_asset])
        await session.commit()
        
        print("Database seeded successfully with admin user, soc user, and sample asset.")

if __name__ == "__main__":
    asyncio.run(seed_database())
