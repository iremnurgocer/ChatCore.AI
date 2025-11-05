# -*- coding: utf-8 -*-
"""
Module: Migrate Old Database Conversations
Description: Migrates conversations and messages from sessions.json (TinyDB) to PostgreSQL
"""
import sys
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from core.database import sync_engine, init_database
from core.config import get_settings
from models.user_model import User
from models.conversation_model import Conversation
from models.message_model import Message, MessageRole

settings = get_settings()


def normalize_username(username: str) -> str:
    """Normalize username"""
    return username.strip().casefold()


def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string"""
    try:
        # Try ISO format
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Try other formats
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        # Fallback to now
        return datetime.utcnow()


def migrate_conversations():
    """Migrate conversations and messages from sessions.json"""
    print("\n" + "=" * 60)
    print("Migrating Conversations from Old Database")
    print("=" * 60)
    
    if sync_engine is None:
        init_database()
    
    if sync_engine is None:
        print("\nERROR: Database not configured. Set DATABASE_URL in .env")
        return False
    
    # Load old data
    sessions_file = Path(__file__).parent.parent / "data" / "sessions.json"
    
    if not sessions_file.exists():
        print(f"\n[SKIP] sessions.json not found at {sessions_file}")
        return False
    
    print(f"\nLoading data from {sessions_file}...")
    
    try:
        with open(sessions_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
    except Exception as e:
        print(f"\nERROR: Failed to load sessions.json: {e}")
        return False
    
    conversations_data = old_data.get("conversations", {})
    chat_history = old_data.get("chat_history", {})
    
    if not conversations_data:
        print("\n[SKIP] No conversations found in old database")
        return False
    
    print(f"\nFound {len(conversations_data)} conversations and {len(chat_history)} messages")
    
    # Create user mapping (username -> user_id)
    user_map = {}
    
    with Session(sync_engine) as session:
        # Get all users
        users = session.exec(select(User)).all()
        for user in users:
            user_map[user.username] = user.id
        
        # Map old usernames to new user IDs
        old_users = old_data.get("users", {})
        for old_user_id, old_user_data in old_users.items():
            old_username = old_user_data.get("username", "").strip()
            normalized = normalize_username(old_username)
            
            # Find matching user
            matched_user = None
            for username, user_id in user_map.items():
                if normalize_username(username) == normalized:
                    matched_user = user_id
                    break
            
            if matched_user:
                user_map[normalized] = matched_user
            else:
                print(f"[WARN] User '{old_username}' not found in new database, skipping conversations")
        
        migrated_conv_count = 0
        migrated_msg_count = 0
        skipped_conv_count = 0
        
        # Migrate conversations
        for old_conv_id, conv_data in conversations_data.items():
            conversation_id = conv_data.get("conversation_id")
            old_username = conv_data.get("user_id", "").strip()
            normalized_username = normalize_username(old_username)
            
            # Find user ID
            user_id = None
            for username, uid in user_map.items():
                if normalize_username(username) == normalized_username:
                    user_id = uid
                    break
            
            if not user_id:
                print(f"[SKIP] Conversation {conversation_id}: User '{old_username}' not found")
                skipped_conv_count += 1
                continue
            
            # Check if conversation already exists
            existing = session.exec(
                select(Conversation).where(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            ).first()
            
            if existing:
                print(f"[SKIP] Conversation {conversation_id} already exists")
                skipped_conv_count += 1
                continue
            
            # Create conversation
            try:
                created_at = parse_datetime(conv_data.get("created_at", ""))
                updated_at = parse_datetime(conv_data.get("updated_at", ""))
                
                conversation = Conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    title=conv_data.get("title", "Eski Sohbet"),
                    message_count=conv_data.get("message_count", 0),
                    is_active=False,  # Mark old conversations as inactive
                    created_at=created_at,
                    updated_at=updated_at
                )
                
                session.add(conversation)
                session.flush()
                
                migrated_conv_count += 1
                print(f"[OK] Migrated conversation {conversation_id}")
                
                # Migrate messages for this conversation
                conv_msg_count = 0
                for msg_id, msg_data in chat_history.items():
                    if msg_data.get("conversation_id") == conversation_id:
                        try:
                            # Convert role string to enum
                            role_str = msg_data.get("role", "user")
                            if role_str == "user":
                                role = MessageRole.USER
                            else:
                                role = MessageRole.ASSISTANT
                            
                            msg_timestamp = parse_datetime(msg_data.get("timestamp", ""))
                            
                            message = Message(
                                message_id=msg_data.get("message_id", f"old_{msg_id}"),
                                user_id=user_id,
                                conversation_id=conversation.id,  # Use database ID
                                role=role,
                                content=msg_data.get("content", ""),
                                created_at=msg_timestamp
                            )
                            
                            session.add(message)
                            conv_msg_count += 1
                            migrated_msg_count += 1
                            
                        except Exception as e:
                            print(f"[WARN] Failed to migrate message {msg_id}: {e}")
                
                if conv_msg_count > 0:
                    # Update message count
                    conversation.message_count = conv_msg_count
                    print(f"  [OK] Migrated {conv_msg_count} messages")
                
            except Exception as e:
                print(f"[FAIL] Failed to migrate conversation {conversation_id}: {e}")
                session.rollback()
                continue
        
        session.commit()
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Conversations migrated: {migrated_conv_count}")
    print(f"  Messages migrated: {migrated_msg_count}")
    print(f"  Conversations skipped: {skipped_conv_count}")
    print("=" * 60)
    
    if migrated_conv_count > 0:
        print("\n[SUCCESS] Migration completed!")
        return True
    else:
        print("\n[WARNING] No conversations migrated")
        return False


def main():
    """Main function"""
    success = migrate_conversations()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

