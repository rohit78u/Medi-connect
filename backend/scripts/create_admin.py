"""Create or promote a local MediConnect administrator account.

Usage:
    python -m scripts.create_admin --email admin@mediconnect.ai --name "MediConnect Admin"

The password is entered interactively and is never stored in this source file.
Run this from the backend directory with the backend environment configured.
"""

import argparse
import asyncio
import getpass

from sqlalchemy import select

import app.db.base  # noqa: F401
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import Role, User


async def main(email: str, full_name: str, password: str) -> None:
    async with AsyncSessionLocal() as db:
        role = (await db.execute(select(Role).where(Role.name == "ADMIN"))).scalars().first()
        if not role:
            role = Role(name="ADMIN", description="Platform administrator")
            db.add(role)
            await db.flush()

        user = (await db.execute(select(User).where(User.email == email.lower()))).scalars().first()
        if user:
            user.full_name = full_name
            user.hashed_password = get_password_hash(password)
        else:
            user = User(
                email=email.lower(),
                full_name=full_name,
                hashed_password=get_password_hash(password),
                is_verified=True,
                is_superuser=True,
            )
            db.add(user)
            await db.flush()

        user.is_active = True
        user.is_verified = True
        user.is_superuser = True
        if role not in user.roles:
            user.roles.append(role)

        await db.commit()
        print(f"Admin account ready: {email.lower()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create/promote a MediConnect admin account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="MediConnect Admin")
    args = parser.parse_args()
    password = getpass.getpass("Admin password: ")
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters.")
    asyncio.run(main(args.email, args.name, password))
