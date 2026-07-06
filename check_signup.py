import asyncio
import traceback
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.models.user import User
from app.core.security import get_password_hash

async def simulate_signup():
    url = "postgresql+asyncpg://fyfitnative_user:zGDfPCeSPoWfdqtvR5FQEb3Ec2Jm9Nc4@dpg-d956hc0js32c73fg8dt0-a.oregon-postgres.render.com/fyfitnative"
    engine = create_async_engine(url)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    email = "test_test_user@fyfit.com"
    password = "TestPassword123"
    full_name = "Simulation Test User"
    
    print("Simulating signup step-by-step...")
    async with AsyncSessionLocal() as db:
        try:
            print("1. Querying if user exists...")
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalars().first()
            print(f"   Existing user: {existing_user}")
            
            if existing_user:
                print("   User already exists, we will try to delete it to keep test clean...")
                await db.delete(existing_user)
                await db.commit()
                print("   Deleted existing test user.")
            
            print("2. Generating password hash...")
            pwd_hash = get_password_hash(password)
            print(f"   Hash: {pwd_hash}")
            
            print("3. Creating User model instance...")
            new_user = User(
                email=email,
                password_hash=pwd_hash,
                first_name=full_name,
                phone=None
            )
            
            print("4. Adding user to session...")
            db.add(new_user)
            
            print("5. Committing transaction...")
            await db.commit()
            print("   Committed successfully!")
            
            print("6. Refreshing instance...")
            await db.refresh(new_user)
            print(f"   Refreshed! New user ID: {new_user.id}")
            
        except Exception as e:
            print("\n!!! ERROR ENCOUNTERED !!!")
            print(e)
            traceback.print_exc()
        finally:
            await db.close()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(simulate_signup())
