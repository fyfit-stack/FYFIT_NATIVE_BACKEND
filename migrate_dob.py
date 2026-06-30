import asyncio
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import urllib.parse

async def run_migration():
    # Init Firebase
    cred = credentials.Certificate("firebase-credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    # Init Postgres
    engine = create_async_engine("postgresql+asyncpg://fyfit:fyfit@postgres:5432/fyfit")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    users_ref = db.collection("users").stream()
    
    async with async_session() as session:
        for doc in users_ref:
            data = doc.to_dict()
            email = data.get("email")
            age = data.get("age") # "18-10-1978"
            if email and age:
                try:
                    # Parse DD-MM-YYYY
                    parsed_date = datetime.strptime(age, "%d-%m-%Y").date()
                    print(f"Migrating DOB for {email}: {parsed_date}")
                    await session.execute(
                        text("UPDATE users SET date_of_birth = :dob WHERE email = :email"),
                        {"dob": parsed_date, "email": email}
                    )
                except Exception as e:
                    print(f"Failed to parse age for {email}: {e}")
        await session.commit()
    print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(run_migration())
