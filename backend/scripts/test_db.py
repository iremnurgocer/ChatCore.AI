# -*- coding: utf-8 -*-
"""
Module: Database Test Script
Description: Tests database connection, tables, and data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select, text
from core.database import sync_engine, init_database, async_engine
from core.config import get_settings
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message
from models.document_model import Document
import asyncio

settings = get_settings()


def test_sync_connection():
    """Test synchronous database connection"""
    print("\n" + "=" * 60)
    print("Testing Synchronous Database Connection")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\n[FAIL] Database not configured. Set DATABASE_URL in .env")
        return False
    
    try:
        with Session(sync_engine) as session:
            # Test connection
            result = session.exec(text("SELECT 1"))
            result.first()
            print("[OK] Synchronous connection successful")
            return True
    except Exception as e:
        print(f"[FAIL] Synchronous connection failed: {e}")
        return False


async def test_async_connection():
    """Test asynchronous database connection"""
    print("\n" + "=" * 60)
    print("Testing Asynchronous Database Connection")
    print("=" * 60)
    
    if async_engine is None:
        init_database()
    
    if async_engine is None:
        print("\n[FAIL] Database not configured. Set DATABASE_URL in .env")
        return False
    
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            print("[OK] Asynchronous connection successful")
            return True
    except Exception as e:
        print(f"[FAIL] Asynchronous connection failed: {e}")
        return False


def test_tables():
    """Test if all tables exist"""
    print("\n" + "=" * 60)
    print("Testing Database Tables")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\n[FAIL] Database not configured")
        return False
    
    tables = ["users", "conversations", "messages", "refresh_tokens", "sessions", "documents"]
    all_exist = True
    
    with Session(sync_engine) as session:
        for table in tables:
            try:
                result = session.exec(text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"))
                exists = result.first()
                if exists:
                    print(f"[OK] Table '{table}' exists")
                else:
                    print(f"[FAIL] Table '{table}' does not exist")
                    all_exist = False
            except Exception as e:
                print(f"[FAIL] Error checking table '{table}': {e}")
                all_exist = False
    
    return all_exist


def test_users():
    """Test user records"""
    print("\n" + "=" * 60)
    print("Testing User Records")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\n[FAIL] Database not configured")
        return False
    
    try:
        with Session(sync_engine) as session:
            users = session.exec(select(User)).all()
            user_count = len(users)
            
            print(f"[OK] Found {user_count} user(s)")
            
            if user_count == 0:
                print("[WARN] No users found. Run 'python scripts/seed_users.py' to create default users.")
                return False
            
            print("\nUser Details:")
            for user in users:
                print(f"  - ID: {user.id}, Username: {user.username}, Admin: {user.is_admin}, Active: {user.is_active}")
            
            return True
    except Exception as e:
        print(f"[FAIL] Error querying users: {e}")
        return False


def test_data_counts():
    """Test data counts for all tables"""
    print("\n" + "=" * 60)
    print("Testing Data Counts")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\n[FAIL] Database not configured")
        return False
    
    try:
        with Session(sync_engine) as session:
            # Count users
            user_count = len(session.exec(select(User)).all())
            print(f"[OK] Users: {user_count}")
            
            # Count conversations
            conv_count = len(session.exec(select(Conversation)).all())
            print(f"[OK] Conversations: {conv_count}")
            
            # Count messages
            msg_count = len(session.exec(select(Message)).all())
            print(f"[OK] Messages: {msg_count}")
            
            # Count documents
            doc_count = len(session.exec(select(Document)).all())
            print(f"[OK] Documents: {doc_count}")
            
            return True
    except Exception as e:
        print(f"[FAIL] Error counting data: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ChatCore.AI - Database Connection Test")
    print("=" * 60)
    
    results = []
    
    # Test sync connection
    results.append(("Sync Connection", test_sync_connection()))
    
    # Test async connection
    results.append(("Async Connection", asyncio.run(test_async_connection())))
    
    # Test tables
    results.append(("Tables", test_tables()))
    
    # Test users
    results.append(("Users", test_users()))
    
    # Test data counts
    results.append(("Data Counts", test_data_counts()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())

