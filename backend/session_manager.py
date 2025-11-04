"""
Session ve Konuşma Hafızası Yönetimi
Kullanıcı bazlı konuşma geçmişi yönetimi - TinyDB ile kalıcı depolama
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from pathlib import Path
import os
import uuid

class SessionManager:
    """Kullanıcı session'larını ve konuşma geçmişini yönetir - TinyDB ile kalıcı"""
    
    def __init__(self, max_history: int = 100, session_timeout: int = 7200):
        # TinyDB dosya yolu
        db_path = Path(__file__).parent / "data" / "sessions.json"
        db_path.parent.mkdir(exist_ok=True)
        
        self.db = TinyDB(str(db_path))
        self.sessions_table = self.db.table("sessions")
        self.chat_history_table = self.db.table("chat_history")
        self.conversations_table = self.db.table("conversations")  # Yeni: conversation yönetimi
        self.max_history = max_history
        self.session_timeout = session_timeout  # saniye cinsinden
        self.Query = Query()
    
    def get_or_create_session(self, user_id: str, token: Optional[str] = None) -> Dict:
        """Session'ı getirir veya oluşturur - TinyDB'den kalıcı"""
        now = datetime.now()
        now_iso = now.isoformat()
        
        # TinyDB'den session'ı ara
        result = self.sessions_table.search(self.Query.user_id == user_id)
        
        if result:
            session_data = result[0]
            last_activity_str = session_data.get("last_activity", now_iso)
            
            # Eski session'larda eksik alanları ekle
            updated = False
            if "viewed_procedures" not in session_data:
                session_data["viewed_procedures"] = []
                updated = True
            if "active_conversation_id" not in session_data:
                # Eski session için varsayılan conversation oluştur
                default_conv_id = self.create_conversation(user_id, "Yeni Sohbet")
                session_data["active_conversation_id"] = default_conv_id
                updated = True
            
            if updated:
                self.sessions_table.update(
                    {
                        "viewed_procedures": session_data.get("viewed_procedures", []),
                        "active_conversation_id": session_data.get("active_conversation_id")
                    },
                    self.Query.user_id == user_id
                )
            
            # String'den datetime'a çevir
            try:
                if isinstance(last_activity_str, str):
                    last_activity = datetime.fromisoformat(last_activity_str)
                else:
                    last_activity = now
            except:
                last_activity = now
            
            # Timeout kontrolü
            time_diff = now - last_activity
            if time_diff.total_seconds() > self.session_timeout:
                # Süresi dolmuş session'ı sil
                self.sessions_table.remove(self.Query.user_id == user_id)
                # Yeni session oluştur
                return self._create_new_session(user_id, token, now_iso)
            
            # Son aktivite zamanını güncelle
            self.sessions_table.update(
                {"last_activity": now_iso},
                self.Query.user_id == user_id
            )
            
            # Token varsa güncelle
            if token:
                self.sessions_table.update(
                    {"token": token},
                    self.Query.user_id == user_id
                )
            
            return session_data
        else:
            # Yeni session oluştur
            return self._create_new_session(user_id, token, now_iso)
    
    def _create_new_session(self, user_id: str, token: Optional[str], now_iso: str) -> Dict:
        """Yeni session oluşturur"""
        # Varsayılan conversation oluştur
        default_conv_id = self.create_conversation(user_id, "Yeni Sohbet")
        
        session_data = {
            "user_id": user_id,
            "token": token,
            "created_at": now_iso,
            "last_activity": now_iso,
            "context": {},
            "viewed_procedures": [],  # Görüntülenen prosedür ID'leri
            "active_conversation_id": default_conv_id  # Aktif conversation
        }
        self.sessions_table.insert(session_data)
        return session_data
    
    def add_message(self, user_id: str, role: str, content: str, conversation_id: Optional[str] = None):
        """Session'a mesaj ekler - TinyDB'ye kalıcı olarak kaydeder"""
        # Conversation ID yoksa aktif conversation'ı kullan
        if not conversation_id:
            conversation_id = self.get_active_conversation_id(user_id)
            # Aktif conversation da yoksa yeni oluştur
            if not conversation_id:
                conversation_id = self.create_conversation(user_id)
                self.set_active_conversation(user_id, conversation_id)
        
        # Conversation'a mesaj ekle
        self.add_message_to_conversation(user_id, conversation_id, role, content)
    
    def get_conversation_history(self, user_id: str, limit: Optional[int] = None, conversation_id: Optional[str] = None) -> List[Dict]:
        """LLM formatında konuşma geçmişini getirir - TinyDB'den"""
        # Conversation ID belirtilmişse onu kullan
        if conversation_id:
            return self.get_conversation_history_by_id(conversation_id, user_id, limit)
        
        # Yoksa aktif conversation'ı kullan
        active_conv_id = self.get_active_conversation_id(user_id)
        if active_conv_id:
            return self.get_conversation_history_by_id(active_conv_id, user_id, limit)
        
        # Aktif conversation da yoksa tüm mesajları getir (eski format için backward compatibility)
        messages = self.chat_history_table.search(self.Query.user_id == user_id)
        messages = sorted(messages, key=lambda x: x.get("timestamp", ""))
        if limit:
            messages = messages[-limit:]
        
        history = []
        for msg in messages:
            history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return history
    
    def get_context(self, user_id: str) -> Dict:
        """Session context'ini getirir"""
        session = self.get_or_create_session(user_id)
        return session.get("context", {})
    
    def update_context(self, user_id: str, key: str, value: any):
        """Context'i günceller - TinyDB'ye kaydeder"""
        session = self.get_or_create_session(user_id)
        context = session.get("context", {})
        context[key] = value
        
        self.sessions_table.update(
            {"context": context},
            self.Query.user_id == user_id
        )
    
    def clear_session(self, user_id: str):
        """Session'ı temizler - TinyDB'den siler"""
        # Session'ı temizle
        self.sessions_table.remove(self.Query.user_id == user_id)
        # Chat geçmişini de temizle
        self.chat_history_table.remove(self.Query.user_id == user_id)
        # Conversation'ları da temizle
        self.conversations_table.remove(self.Query.user_id == user_id)
    
    def session_exists(self, user_id: str) -> bool:
        """Session var mı kontrol et"""
        result = self.sessions_table.search(self.Query.user_id == user_id)
        return len(result) > 0
    
    def get_session_by_token(self, token: str) -> Optional[Dict]:
        """Token'a göre session'ı getirir"""
        result = self.sessions_table.search(self.Query.token == token)
        if result:
            return result[0]
        return None
    
    def update_last_activity(self, user_id: str):
        """Son aktivite zamanını günceller"""
        now_iso = datetime.now().isoformat()
        self.sessions_table.update(
            {"last_activity": now_iso},
            self.Query.user_id == user_id
        )
    
    def mark_procedure_viewed(self, user_id: str, procedure_id: int):
        """Prosedürün görüntülendiğini işaretle"""
        session = self.get_or_create_session(user_id)
        viewed = session.get("viewed_procedures", [])
        
        if procedure_id not in viewed:
            viewed.append(procedure_id)
            self.sessions_table.update(
                {"viewed_procedures": viewed},
                self.Query.user_id == user_id
            )
    
    def get_viewed_procedures(self, user_id: str) -> List[int]:
        """Kullanıcının görüntülediği prosedür ID'lerini döndür"""
        session = self.get_or_create_session(user_id)
        return session.get("viewed_procedures", [])
    
    def get_session_summary(self, user_id: str) -> str:
        """LLM için son mesajların özetini getirir"""
        messages = self.get_conversation_history(user_id)
        if not messages:
            return ""

        # Son 3 mesajı al
        recent = messages[-3:]
        summary = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
        return summary
    
    # ========== CONVERSATION MANAGEMENT ==========
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> str:
        """
        Yeni conversation oluşturur - benzersiz ID döner
        
        Her kullanıcı için tamamen izole conversation'lar oluşturur.
        ChatGPT gibi her conversation ayrı bir sohbet gibi çalışır.
        
        Args:
            user_id: Kullanıcı ID (conversation'ın sahibi)
            title: Conversation başlığı (opsiyonel, ilk mesajdan otomatik oluşturulur)
            
        Returns:
            Conversation ID (8 karakterlik benzersiz ID)
        """
        conversation_id = str(uuid.uuid4())[:8]  # Kısa ID (8 karakter)
        now_iso = datetime.now().isoformat()
        
        # İlk mesajdan başlık oluştur (title yoksa)
        if not title:
            title = "Yeni Sohbet"
        
        conversation = {
            "conversation_id": conversation_id,
            "user_id": user_id,  # Her conversation bir kullanıcıya ait
            "title": title,
            "created_at": now_iso,
            "updated_at": now_iso,
            "message_count": 0
        }
        
        self.conversations_table.insert(conversation)
        
        return conversation_id
    
    def cleanup_empty_conversations(self, user_id: str):
        """Boş conversation'ları temizle (0 mesaj)"""
        conversations = self.conversations_table.search(self.Query.user_id == user_id)
        for conv in conversations:
            if conv.get("message_count", 0) == 0:
                # Boş conversation'ı sil
                self.conversations_table.remove(
                    (self.Query.conversation_id == conv.get("conversation_id")) & 
                    (self.Query.user_id == user_id)
                )
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Kullanıcının tüm conversation'larını getirir"""
        conversations = self.conversations_table.search(self.Query.user_id == user_id)
        # En son güncellenenler önce gelsin
        conversations = sorted(conversations, key=lambda x: x.get("updated_at", ""), reverse=True)
        return conversations
    
    def get_conversation_owner(self, conversation_id: str) -> Optional[str]:
        """Conversation'ın sahibi olan user_id'yi döndürür"""
        result = self.conversations_table.search(self.Query.conversation_id == conversation_id)
        if result:
            return result[0].get("user_id")
        return None
    
    def get_user_token_from_conversation(self, conversation_id: str) -> Optional[str]:
        """Conversation ID'den user_id ve token'ı al"""
        owner_id = self.get_conversation_owner(conversation_id)
        if not owner_id:
            return None
        
        # User'ın session'ını al
        session = self.get_or_create_session(owner_id)
        token = session.get("token")
        return token if token else None
    
    def get_conversation(self, conversation_id: str, user_id: str = None) -> Optional[Dict]:
        """
        Conversation bilgilerini getirir - KULLANICI İZOLASYONU ile
        
        Args:
            conversation_id: Conversation ID
            user_id: Kullanıcı ID (GÜVENLİK: Conversation'ın sahibi olmalı)
            
        Returns:
            Conversation dictionary'si veya None (kullanıcıya ait değilse)
        """
        result = self.conversations_table.search(self.Query.conversation_id == conversation_id)
        if not result:
            return None
        
        conversation = result[0]
        
        # GÜVENLİK: user_id belirtilmişse, conversation'ın kullanıcıya ait olduğunu kontrol et
        if user_id:
            conv_owner = conversation.get("user_id")
            if conv_owner != user_id:
                # Conversation ba�ka bir kullan�c�ya ait - eri�im reddedildi
                return None
        
        return conversation
    
    def update_conversation_title(self, conversation_id: str, user_id: str, title: str):
        """Conversation başlığını güncelle (ilk mesajdan)"""
        self.conversations_table.update(
            {"title": title, "updated_at": datetime.now().isoformat()},
            (self.Query.conversation_id == conversation_id) & (self.Query.user_id == user_id)
        )
    
    def add_message_to_conversation(self, user_id: str, conversation_id: str, role: str, content: str):
        """Conversation'a mesaj ekler"""
        now_iso = datetime.now().isoformat()
        
        message = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": now_iso,
            "message_id": str(uuid.uuid4())[:12]  # Her mesaj için benzersiz ID
        }
        
        # Chat history tablosuna ekle
        self.chat_history_table.insert(message)
        
        # Conversation'ı güncelle
        conv = self.get_conversation(conversation_id, user_id)
        if conv:
            message_count = conv.get("message_count", 0) + 1
            # İlk mesajdan başlık oluştur
            if message_count == 1 and role == "user":
                # İlk mesajdan başlık oluştur (max 50 karakter)
                title = content[:50] + ("..." if len(content) > 50 else "")
                self.conversations_table.update(
                    {"title": title, "message_count": message_count, "updated_at": now_iso},
                    (self.Query.conversation_id == conversation_id) & (self.Query.user_id == user_id)
                )
            else:
                self.conversations_table.update(
                    {"message_count": message_count, "updated_at": now_iso},
                    (self.Query.conversation_id == conversation_id) & (self.Query.user_id == user_id)
                )
    
    def get_conversation_history_by_id(self, conversation_id: str, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Belirli bir conversation'ın mesaj geçmişini getirir - KULLANICI İZOLASYONU ile
        
        Args:
            conversation_id: Conversation ID
            user_id: Kullanıcı ID (GÜVENLİK: Conversation'ın sahibi olmalı)
            limit: Maksimum mesaj sayısı
            
        Returns:
            Mesaj listesi (LLM formatında)
        """
        # GÜVENLİK: Conversation'ın kullanıcıya ait olduğunu kontrol et
        conv = self.get_conversation(conversation_id, user_id)
        if not conv:
            return []  # Bo� liste d�nd�r (g�venlik i�in)
        
        # Conversation'a ait mesajları getir
        messages = self.chat_history_table.search(
            (self.Query.conversation_id == conversation_id) & 
            (self.Query.user_id == user_id)
        )
        
        messages = sorted(messages, key=lambda x: x.get("timestamp", ""))
        if limit:
            messages = messages[-limit:]
        
        history = []
        for msg in messages:
            history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return history
    
    def delete_conversation(self, conversation_id: str, user_id: str):
        """Conversation'ı sil (mesajlarla birlikte)"""
        # Conversation'ı sil
        self.conversations_table.remove(
            (self.Query.conversation_id == conversation_id) & (self.Query.user_id == user_id)
        )
        # Mesajları sil
        self.chat_history_table.remove(
            (self.Query.conversation_id == conversation_id) & (self.Query.user_id == user_id)
        )
    
    def get_active_conversation_id(self, user_id: str) -> Optional[str]:
        """Session'dan aktif conversation ID'yi getirir"""
        session = self.get_or_create_session(user_id)
        return session.get("active_conversation_id")
    
    def set_active_conversation(self, user_id: str, conversation_id: str):
        """Aktif conversation'ı ayarla"""
        session = self.get_or_create_session(user_id)
        session["active_conversation_id"] = conversation_id
        self.sessions_table.update(
            {"active_conversation_id": conversation_id},
            self.Query.user_id == user_id
        )

# Global session manager instance
session_manager = SessionManager()
