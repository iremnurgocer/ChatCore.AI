# -*- coding: utf-8 -*-
"""
Session Manager modülü için testler
"""
import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from session_manager import session_manager

def test_create_conversation():
    """Conversation oluşturma testi"""
    user_id = "test_user"
    conv_id = session_manager.create_conversation(user_id, "Test Conversation")
    
    assert conv_id is not None
    assert len(conv_id) > 0
    
    # Conversation'ı kontrol et
    conv = session_manager.get_conversation(conv_id, user_id)
    assert conv is not None
    assert conv["user_id"] == user_id

def test_add_message():
    """Mesaj ekleme testi"""
    user_id = "test_user"
    conv_id = session_manager.create_conversation(user_id)
    
    session_manager.add_message(user_id, "user", "Merhaba", conversation_id=conv_id)
    session_manager.add_message(user_id, "assistant", "Merhaba!", conversation_id=conv_id)
    
    history = session_manager.get_conversation_history(user_id, conversation_id=conv_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

def test_user_isolation():
    """Kullanıcı izolasyonu testi"""
    user1 = "user1"
    user2 = "user2"
    
    conv1 = session_manager.create_conversation(user1)
    conv2 = session_manager.create_conversation(user2)
    
    # User1, User2'nin conversation'ını görmemeli
    conv = session_manager.get_conversation(conv2, user1)
    assert conv is None
    
    # User2, User1'in conversation'ını görmemeli
    conv = session_manager.get_conversation(conv1, user2)
    assert conv is None

