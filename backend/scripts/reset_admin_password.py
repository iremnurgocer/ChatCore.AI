# -*- coding: utf-8 -*-
"""
Module: Reset Admin Password Script
Description: Resets admin password to '1234' in PostgreSQL. Idempotent.
"""
import sys
from pathlib import Path
from typing import Optional
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from core.database import sync_engine, init_database
from models.user_model import User
import hashlib
import binascii
import secrets

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


def reset_admin_password():
    """Reset admin password to '1234'"""
    print("=" * 60)
    print("Reset Admin Password")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\nERROR: Database not configured. Set DATABASE_URL in .env")
        return
    
    admin_password = "1234"
    
    with Session(sync_engine) as session:
        # Find admin user
        admin_user = session.exec(
            select(User).where(User.username == "admin")
        ).first()
        
        if not admin_user:
            print("\nERROR: Admin user not found!")
            print("Please run 'python backend/scripts/seed_users.py' first.")
            return
        
        # Reset password
        password_hash, salt = hash_password(admin_password)
        
        admin_user.password_hash = password_hash
        admin_user.salt = salt
        
        session.add(admin_user)
        session.commit()
        
        print(f"\n[SUCCESS] Admin password reset to '{admin_password}'")
        print(f"  Username: admin")
        print(f"  Password: {admin_password}")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    reset_admin_password()

