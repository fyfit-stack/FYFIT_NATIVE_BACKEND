import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    # Use the async pg url
    url = "postgresql+asyncpg://fyfitnative_user:zGDfPCeSPoWfdqtvR5FQEb3Ec2Jm9Nc4@dpg-d956hc0js32c73fg8dt0-a.oregon-postgres.render.com/fyfitnative"
    print(f"Connecting to database to check tables...")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            # Query tables
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
            ))
            tables = result.fetchall()
            print("Tables found in database:")
            for t in tables:
                print(f" - {t[0]}")
            if not tables:
                print("No tables found! The database is empty.")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
