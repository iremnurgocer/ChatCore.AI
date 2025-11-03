"""
Session ve Konuşma Hafızası Yönetimi
Kullanıcı bazlı konuşma geçmişi yönetimi - TinyDB ile kalıcı depolama
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from pathlib import Path
import os

class SessionManager:
    """Kullanıcı session'larını ve konuşma geçmişini yönetir - TinyDB ile kalıcı"""
    
    def __init__(self, max_history: int = 100, session_timeout: int = 7200):
        # TinyDB dosya yolu
        db_path = Path(__file__).parent / "data" / "sessions.json"
        db_path.parent.mkdir(exist_ok=True)
        
        self.db = TinyDB(str(db_path))
        self.sessions_table = self.db.table("sessions")
        self.chat_history_table = self.db.table("chat_history")
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
            
            # Eski session'larda viewed_procedures yoksa ekle
            if "viewed_procedures" not in session_data:
                session_data["viewed_procedures"] = []
                self.sessions_table.update(
                    {"viewed_procedures": []},
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
        session_data = {
            "user_id": user_id,
            "token": token,
            "created_at": now_iso,
            "last_activity": now_iso,
            "context": {},
            "viewed_procedures": []  # Görüntülenen prosedür ID'leri
        }
        self.sessions_table.insert(session_data)
        return session_data
    
    def add_message(self, user_id: str, role: str, content: str):
        """Session'a mesaj ekler - TinyDB'ye kalıcı olarak kaydeder"""
        now_iso = datetime.now().isoformat()
        
        message = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": now_iso
        }
        
        # Chat history tablosuna ekle
        self.chat_history_table.insert(message)
        
        # Eski mesajları temizle (max_history kontrolü)
        all_messages = self.chat_history_table.search(self.Query.user_id == user_id)
        if len(all_messages) > self.max_history:
            # En eski mesajları sil
            sorted_messages = sorted(all_messages, key=lambda x: x.get("timestamp", ""))
            messages_to_delete = sorted_messages[:-self.max_history]
            for msg in messages_to_delete:
                self.chat_history_table.remove(self.Query.timestamp == msg["timestamp"])
    
    def get_conversation_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """LLM formatında konuşma geçmişini getirir - TinyDB'den"""
        # TinyDB'den kullanıcının mesajlarını al
        messages = self.chat_history_table.search(self.Query.user_id == user_id)
        
        # Timestamp'e göre sırala
        messages = sorted(messages, key=lambda x: x.get("timestamp", ""))
        
        # Limit varsa son N mesajı al
        if limit:
            messages = messages[-limit:]
        
        # LLM formatına dönüştür (role/content dict'leri)
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
        self.sessions_table.remove(self.Query.user_id == user_id)
        # Chat geçmişini de temizle
        self.chat_history_table.remove(self.Query.user_id == user_id)
    
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

# Global session manager instance
session_manager = SessionManager()
