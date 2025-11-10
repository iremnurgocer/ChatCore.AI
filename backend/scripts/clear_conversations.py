# -*- coding: utf-8 -*-
"""
Clear all conversations and messages from database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import sync_engine, get_sync_session
from models.conversation_model import Conversation
from models.message_model import Message

def clear_all_conversations():
    """Clear all conversations and messages"""
    print("=" * 60)
    print("Tüm sohbet geçmişini temizleme")
    print("=" * 60)
    
    with get_sync_session() as session:
        try:
            # Count before deletion
            conv_count = session.query(Conversation).count()
            msg_count = session.query(Message).count()
            
            print(f"\nMevcut durum:")
            print(f"  - Conversation sayısı: {conv_count}")
            print(f"  - Mesaj sayısı: {msg_count}")
            
            if conv_count == 0 and msg_count == 0:
                print("\nZaten temiz! Silinecek bir şey yok.")
                return
            
            # Delete all messages first (CASCADE should handle this, but explicit)
            print("\nMesajlar siliniyor...")
            session.execute(text("DELETE FROM messages"))
            deleted_messages = session.query(Message).count()
            print(f"  [OK] {msg_count} mesaj silindi")
            
            # Delete all conversations
            print("\nConversation'lar siliniyor...")
            session.execute(text("DELETE FROM conversations"))
            deleted_convs = session.query(Conversation).count()
            print(f"  [OK] {conv_count} conversation silindi")
            
            # Commit
            session.commit()
            
            print("\n" + "=" * 60)
            print("Temizleme tamamlandı!")
            print("=" * 60)
            print(f"\nSilinen:")
            print(f"  - {conv_count} conversation")
            print(f"  - {msg_count} mesaj")
            
        except Exception as e:
            session.rollback()
            print(f"\n[HATA] Temizleme başarısız: {e}")
            raise

if __name__ == "__main__":
    clear_all_conversations()

