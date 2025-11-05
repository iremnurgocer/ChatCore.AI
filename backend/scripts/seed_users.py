# -*- coding: utf-8 -*-
"""
Module: Seed Users Script
Description: Creates default users (admin, user2, user3) in PostgreSQL. Idempotent.
"""
import sys
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from core.database import sync_engine, init_database
from core.config import get_settings
from models.user_model import User
import hashlib
import binascii
import secrets

settings = get_settings()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password using PBKDF2-HMAC-SHA256"""
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
        salt_hex = salt_bytes.hex()
    else:
        salt_bytes = binascii.unhexlify(salt)
        salt_hex = salt
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        100000
    )
    
    return password_hash.hex(), salt_hex


def normalize_username(username: str) -> str:
    """Normalize username"""
    return username.strip().casefold()


def seed_users():
    """Seed default users"""
    print("=" * 60)
    print("Seeding Default Users")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\nERROR: Database not configured. Set DATABASE_URL in .env")
        return
    
    default_users = [
        {"username": "admin", "password": "1234", "is_admin": True},
        {"username": "user2", "password": "1234", "is_admin": False},
        {"username": "user3", "password": "12345", "is_admin": False},
    ]
    
    created_count = 0
    existing_count = 0
    
    with Session(sync_engine) as session:
        for user_data in default_users:
            username = user_data["username"]
            normalized = normalize_username(username)
            
            # Check if user exists
            existing = session.exec(
                select(User).where(User.username == normalized)
            ).first()
            
            if existing:
                print(f"  [SKIP] User '{username}' already exists (ID: {existing.id})")
                existing_count += 1
                continue
            
            # Create user
            password_hash, salt = hash_password(user_data["password"])
            
            user = User(
                username=normalized,
                password_hash=password_hash,
                salt=salt,
                is_active=True,
                is_admin=user_data["is_admin"]
            )
            
            session.add(user)
            session.flush()
            print(f"  [OK] Created user '{username}' (ID: {user.id})")
            created_count += 1
        
        session.commit()
    
    print("\n" + "=" * 60)
    print(f"Summary: {created_count} created, {existing_count} already existed")
    print("=" * 60)
    print("\n[SUCCESS] Seeding completed!")


if __name__ == "__main__":
    seed_users()
