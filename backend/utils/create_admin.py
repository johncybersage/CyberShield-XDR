"""
CyberShield XDR — Admin User Seeder
Creates the initial admin user on first deployment.

Usage:
    python -m backend.utils.create_admin
    python -m backend.utils.create_admin --email admin@company.com --password Admin@123!
"""
import argparse
import asyncio

from sqlalchemy import select

from backend.auth.security import hash_password
from backend.config.logging_config import get_logger, setup_logging
from backend.database.session import AsyncSessionLocal, init_db
from backend.models.user import User, UserRole

setup_logging()
logger = get_logger(__name__)


async def create_admin(email: str, username: str, full_name: str, password: str) -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.info(f"Admin user already exists: {email}")
            return

        admin = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        session.add(admin)
        await session.commit()
        logger.info(f"Admin user created: {email} [{admin.id}]")
        print("\n✅ Admin user created successfully!")
        print(f"   Email:    {email}")
        print(f"   Username: {username}")
        print("   Role:     admin\n")


def main():
    parser = argparse.ArgumentParser(description="Create CyberShield admin user")
    parser.add_argument("--email",     default="admin@cybershield.com")
    parser.add_argument("--username",  default="admin")
    parser.add_argument("--full-name", default="Platform Administrator")
    parser.add_argument("--password",  default="Admin@123!")
    args = parser.parse_args()

    print("\n🛡️  CyberShield XDR — Admin Setup")
    print(f"Creating admin user: {args.email}\n")

    asyncio.run(create_admin(
        email=args.email,
        username=args.username,
        full_name=args.full_name,
        password=args.password,
    ))


if __name__ == "__main__":
    main()
