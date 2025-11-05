# -*- coding: utf-8 -*-
"""
Module: TinyDB to PostgreSQL Migration Script
Description: Idempotent migration script for migrating TinyDB data to PostgreSQL.
"""
import json
import hashlib
import binascii
import secrets
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from sqlmodel import Session, select
from core.database import sync_engine, init_database
from core.config import get_settings
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message
from models.refresh_token_model import RefreshToken
from models.session_model import Session as SessionModel
from models.document_model import Document

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
    """Normalize username (casefold + strip)"""
    return username.strip().casefold()


def migrate_users(session: Session, users_data: List[Dict]) -> Dict[str, int]:
    """Migrate users from TinyDB to PostgreSQL"""
    print("\n1. Migrating users...")
    user_map = {}
    created_count = 0
    updated_count = 0
    
    for user_data in users_data:
        username = user_data.get("username")
        if not username:
            continue
        
        normalized = normalize_username(username)
        
        # Check if user exists
        existing = session.exec(
            select(User).where(User.username == normalized)
        ).first()
        
        if existing:
            user_map[normalized] = existing.id
            updated_count += 1
            continue
        
        # Get password hash and salt
        password_hash = user_data.get("password_hash")
        salt = user_data.get("salt")
        
        # If no hash, generate one (for default users)
        if not password_hash or not salt:
            # Default passwords for known users
            default_passwords = {
                "admin": "1234",
                "user2": "1234",
                "user3": "12345"
            }
            password = default_passwords.get(normalized, "changeme")
            password_hash, salt = hash_password(password)
        
        user = User(
            username=normalized,
            password_hash=password_hash,
            salt=salt,
            email=user_data.get("email"),
            is_active=user_data.get("is_active", True),
            is_admin=user_data.get("is_admin", False)
        )
        
        session.add(user)
        session.flush()
        user_map[normalized] = user.id
        created_count += 1
        print(f"  ✓ Migrated user: {normalized}")
    
    session.commit()
    print(f"  Summary: {created_count} created, {updated_count} already existed")
    return user_map


def migrate_conversations(
    session: Session,
    conversations_data: List[Dict],
    user_map: Dict[str, int]
) -> Dict[str, int]:
    """Migrate conversations from TinyDB to PostgreSQL"""
    print("\n2. Migrating conversations...")
    conversation_map = {}
    created_count = 0
    skipped_count = 0
    
    for conv_data in conversations_data:
        user_id_str = conv_data.get("user_id")
        conversation_id = conv_data.get("conversation_id")
        
        if not user_id_str or not conversation_id:
            continue
        
        normalized_user = normalize_username(user_id_str)
        if normalized_user not in user_map:
            skipped_count += 1
            continue
        
        user_id = user_map[normalized_user]
        
        # Check if conversation exists
        existing = session.exec(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id
            )
        ).first()
        
        if existing:
            conversation_map[conversation_id] = existing.id
            continue
        
        # Parse dates
        created_at_str = conv_data.get("created_at", datetime.now().isoformat())
        updated_at_str = conv_data.get("updated_at", created_at_str)
        
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except:
            created_at = datetime.now()
        
        try:
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        except:
            updated_at = created_at
        
        conv = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=conv_data.get("title", "Yeni Sohbet"),
            is_active=conv_data.get("is_active", False),
            message_count=conv_data.get("message_count", 0),
            created_at=created_at,
            updated_at=updated_at
        )
        
        session.add(conv)
        session.flush()
        conversation_map[conversation_id] = conv.id
        created_count += 1
    
    session.commit()
    print(f"  Summary: {created_count} created, {skipped_count} skipped (user not found)")
    return conversation_map


def migrate_messages(
    session: Session,
    messages_data: List[Dict],
    user_map: Dict[str, int],
    conversation_map: Dict[str, int]
):
    """Migrate messages from TinyDB to PostgreSQL"""
    print("\n3. Migrating messages...")
    created_count = 0
    skipped_count = 0
    duplicate_count = 0
    
    # Track seen messages by hash to avoid duplicates
    seen_hashes: Set[str] = set()
    
    for msg_data in messages_data:
        user_id_str = msg_data.get("user_id")
        conversation_id = msg_data.get("conversation_id")
        
        if not user_id_str or conversation_id not in conversation_map:
            skipped_count += 1
            continue
        
        normalized_user = normalize_username(user_id_str)
        if normalized_user not in user_map:
            skipped_count += 1
            continue
        
        user_id = user_map[normalized_user]
        conv_db_id = conversation_map[conversation_id]
        
        # Create message hash for duplicate detection
        content = msg_data.get("content", "")
        role = msg_data.get("role", "user")
        timestamp = msg_data.get("timestamp", "")
        msg_hash = hashlib.md5(
            f"{conversation_id}:{timestamp}:{role}:{content}".encode()
        ).hexdigest()
        
        if msg_hash in seen_hashes:
            duplicate_count += 1
            continue
        
        seen_hashes.add(msg_hash)
        
        # Check if message exists by message_id
        message_id = msg_data.get("message_id")
        if message_id:
            existing = session.exec(
                select(Message).where(Message.message_id == message_id)
            ).first()
            if existing:
                duplicate_count += 1
                continue
        
        # Parse timestamp
        timestamp_str = msg_data.get("timestamp", datetime.now().isoformat())
        try:
            created_at = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except:
            created_at = datetime.now()
        
        message = Message(
            message_id=message_id or str(secrets.token_urlsafe(12)),
            user_id=user_id,
            conversation_id=conv_db_id,
            role=role,
            content=content,
            created_at=created_at,
            used_documents=msg_data.get("used_documents"),
            token_count=msg_data.get("token_count")
        )
        
        session.add(message)
        created_count += 1
        
        # Commit in batches
        if created_count % 100 == 0:
            session.commit()
    
    session.commit()
    print(f"  Summary: {created_count} created, {skipped_count} skipped, {duplicate_count} duplicates")
    
    # Update conversation message counts
    print("\n4. Updating conversation message counts...")
    for conv_id, conv_db_id in conversation_map.items():
        count = session.exec(
            select(Message).where(Message.conversation_id == conv_db_id)
        ).all()
        session.exec(
            select(Conversation).where(Conversation.id == conv_db_id)
        ).first().message_count = len(count)
    session.commit()


def migrate_documents(session: Session, data_dir: Path):
    """Migrate company JSON files to documents table"""
    print("\n5. Migrating documents...")
    doc_types = {
        "employees.json": "employee",
        "departments.json": "department",
        "projects.json": "project",
        "procedures.json": "procedure"
    }
    
    created_count = 0
    skipped_count = 0
    
    for filename, doc_type in doc_types.items():
        file_path = data_dir / filename
        if not file_path.exists():
            continue
        
        print(f"  Processing {filename}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"    ✗ Error reading {filename}: {e}")
            continue
        
        if not isinstance(data, list):
            data = [data]
        
        for item in data:
            # Check if document exists (by doc_type and body hash)
            body_str = json.dumps(item, sort_keys=True)
            body_hash = hashlib.md5(body_str.encode()).hexdigest()
            
            existing = session.exec(
                select(Document).where(
                    Document.doc_type == doc_type,
                    Document.body == item  # JSONB comparison
                )
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            doc = Document(
                doc_type=doc_type,
                body=item
            )
            session.add(doc)
            created_count += 1
        
        session.commit()
    
    print(f"  Summary: {created_count} created, {skipped_count} already existed")


def migrate_sessions(
    session: Session,
    sessions_data: List[Dict],
    user_map: Dict[str, int]
):
    """Migrate sessions from TinyDB to PostgreSQL"""
    print("\n6. Migrating sessions...")
    created_count = 0
    skipped_count = 0
    
    for sess_data in sessions_data:
        user_id_str = sess_data.get("user_id")
        if not user_id_str:
            continue
        
        normalized_user = normalize_username(user_id_str)
        if normalized_user not in user_map:
            skipped_count += 1
            continue
        
        user_id = user_map[normalized_user]
        token = sess_data.get("token")
        
        if not token:
            continue
        
        # Generate access_jti from token
        access_jti = hashlib.sha256(token.encode()).hexdigest()[:32]
        
        # Check if session exists
        existing = session.exec(
            select(SessionModel).where(SessionModel.access_jti == access_jti)
        ).first()
        
        if existing:
            continue
        
        # Parse dates
        created_at_str = sess_data.get("created_at", datetime.now().isoformat())
        last_activity_str = sess_data.get("last_activity", created_at_str)
        
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except:
            created_at = datetime.now()
        
        try:
            last_activity = datetime.fromisoformat(last_activity_str.replace("Z", "+00:00"))
        except:
            last_activity = created_at
        
        sess = SessionModel(
            user_id=user_id,
            access_jti=access_jti,
            user_agent=sess_data.get("user_agent"),
            ip_address=sess_data.get("ip_address"),
            created_at=created_at,
            last_activity=last_activity,
            revoked=False
        )
        
        session.add(sess)
        created_count += 1
    
    session.commit()
    print(f"  Summary: {created_count} created, {skipped_count} skipped")


def migrate_tinydb_to_postgresql():
    """Main migration function"""
    print("=" * 60)
    print("TinyDB to PostgreSQL Migration")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\nERROR: Database not configured. Set DATABASE_URL in .env")
        return
    
    data_dir = Path(__file__).parent.parent / "data"
    sessions_file = data_dir / "sessions.json"
    
    if not sessions_file.exists():
        print(f"\nWARNING: {sessions_file} not found. Skipping TinyDB migration.")
        print("Only migrating documents from JSON files...")
        
        with Session(sync_engine) as session:
            migrate_documents(session, data_dir)
            print("\n✅ Migration completed!")
        return
    
    # Load TinyDB data
    print("\nLoading TinyDB data...")
    try:
        with open(sessions_file, "r", encoding="utf-8") as f:
            tinydb_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load TinyDB data: {e}")
        return
    
    # Extract tables
    users_data = tinydb_data.get("_default", {}).get("users", [])
    sessions_data = tinydb_data.get("_default", {}).get("sessions", [])
    conversations_data = tinydb_data.get("_default", {}).get("conversations", [])
    messages_data = tinydb_data.get("_default", {}).get("chat_history", [])
    
    print(f"  Found: {len(users_data)} users, {len(sessions_data)} sessions, "
          f"{len(conversations_data)} conversations, {len(messages_data)} messages")
    
    with Session(sync_engine) as session:
        # Migrate in order
        user_map = migrate_users(session, users_data)
        conversation_map = migrate_conversations(session, conversations_data, user_map)
        migrate_messages(session, messages_data, user_map, conversation_map)
        migrate_sessions(session, sessions_data, user_map)
        migrate_documents(session, data_dir)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    
    with Session(sync_engine) as session:
        user_count = len(session.exec(select(User)).all())
        conv_count = len(session.exec(select(Conversation)).all())
        msg_count = len(session.exec(select(Message)).all())
        sess_count = len(session.exec(select(SessionModel)).all())
        doc_count = len(session.exec(select(Document)).all())
        
        print(f"Users: {user_count}")
        print(f"Conversations: {conv_count}")
        print(f"Messages: {msg_count}")
        print(f"Sessions: {sess_count}")
        print(f"Documents: {doc_count}")
    
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    migrate_tinydb_to_postgresql()

