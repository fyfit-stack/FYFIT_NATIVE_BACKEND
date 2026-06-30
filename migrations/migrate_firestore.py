import os
import sys
import json
from datetime import datetime

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import firebase_admin
from firebase_admin import credentials, firestore
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings

def main():
    print("--- Starting Firestore to Postgres Migration ---")
    
    # 1. Initialize Firebase Admin SDK
    creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "firebase-credentials.json")
    if not os.path.exists(creds_path):
        print(f"ERROR: Cannot find Firebase credentials at {creds_path}")
        return
    
    try:
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Successfully connected to Firestore.")
    except Exception as e:
        print(f"ERROR connecting to Firestore: {e}")
        return

    # 2. Connect to PostgreSQL
    db_url = settings.sync_database_url
    print(f"Connecting to Postgres using: {db_url}")
    
    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        pg_session = SessionLocal()
        print("Successfully connected to PostgreSQL.")
    except Exception as e:
        print(f"ERROR connecting to PostgreSQL: {e}")
        print("Ensure your PostgreSQL database is running (e.g., via docker-compose up).")
        return

    # 3. Fetch and Migrate Users
    users_ref = db.collection("users")
    docs = users_ref.stream()
    
    migrated_count = 0
    skipped_count = 0

    for doc in docs:
        data = doc.to_dict()
        email = data.get("email")
        
        if not email:
            print(f"Skipping document {doc.id} - No email found.")
            skipped_count += 1
            continue
            
        # Check if user already exists in PG
        existing_user = pg_session.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Skipping {email} - Already exists in Postgres.")
            skipped_count += 1
            continue

        print(f"Migrating user: {email}...")
        
        # Hash the raw plaintext password from Firestore
        raw_password = data.get("password")
        hashed_password = None
        if raw_password:
            hashed_password = get_password_hash(raw_password)

        # Parse basic fields
        name = data.get("name")
        phone = data.get("mobileNo")
        gender = data.get("gender")
        profile_url = data.get("profileUrl")
        firebase_uid = data.get("uid", doc.id)

        new_user = User(
            firebase_uid=firebase_uid,
            email=email,
            password_hash=hashed_password,
            first_name=name, # Storing full name in first_name for now
            phone=phone,
            gender=gender,
            profile_pic_url=profile_url
        )
        
        pg_session.add(new_user)
        try:
            pg_session.commit()
            migrated_count += 1
        except IntegrityError:
            pg_session.rollback()
            print(f"Duplicate detected for user {email}. Altering data to ensure migration...")
            if new_user.phone:
                new_user.phone = f"{new_user.phone}_dup"[:20] # Keep within 20 chars
            if new_user.email:
                new_user.email = f"dup_{new_user.email}"
            
            pg_session.add(new_user)
            try:
                pg_session.commit()
                migrated_count += 1
            except Exception as retry_err:
                pg_session.rollback()
                print(f"Still failed to migrate {email}: {retry_err}")
                skipped_count += 1
        except Exception as e:
            pg_session.rollback()
            print(f"Skipping user {email} due to error: {e}")
            skipped_count += 1

    print(f"\n--- Migration Complete ---")
    print(f"Successfully migrated {migrated_count} users to PostgreSQL.")
    print(f"Skipped {skipped_count} users.")
    pg_session.close()

if __name__ == "__main__":
    main()
