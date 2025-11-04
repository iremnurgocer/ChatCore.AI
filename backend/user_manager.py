"""
Kullanıcı Yönetimi Modülü - TinyDB ile Kullanıcı Veritabanı
Kullanıcı bilgilerini güvenli bir şekilde saklar ve yönetir
"""
from typing import Dict, Optional, List
from datetime import datetime
from tinydb import TinyDB, Query
from pathlib import Path
import hashlib
import secrets
import binascii

class UserManager:
    """Kullanıcı yönetimi - TinyDB ile kalıcı depolama"""
    
    def __init__(self):
        # TinyDB dosya yolu
        db_path = Path(__file__).parent / "data" / "sessions.json"
        db_path.parent.mkdir(exist_ok=True)
        
        self.db = TinyDB(str(db_path))
        self.users_table = self.db.table("users")
        self.Query = Query()
        
        # İlk kurulum için varsayılan kullanıcıları oluştur
        self._initialize_default_users()
    
    @staticmethod
    def normalize_username(username: str) -> str:
        """
        Username'i normalize eder - tek bir standardizasyon fonksiyonu
        Strip ve casefold kullanarak tutarlılık sağlar
        
        Args:
            username: Normalize edilecek username
            
        Returns:
            Normalize edilmiş username
        """
        if not username:
            return ""
        return username.strip().casefold()
    
    def _initialize_default_users(self):
        """Varsayılan kullanıcıları oluşturur (eğer yoksa)"""
        default_users = [
            {"username": "admin", "password": "1234"},
            {"username": "user2", "password": "1234"},
            {"username": "user3", "password": "12345"}
        ]
        
        for user_info in default_users:
            username = user_info["username"]
            password = user_info["password"]
            
            # Normalize edilmiş username ile kontrol et
            normalized_username = self.normalize_username(username)
            existing = self.users_table.search(self.Query.username == normalized_username)
            
            if not existing:
                # Yeni kullanıcı oluştur (normalize edilmiş username ile)
                self.create_user(username, password)
            else:
                # Kullanıcı var, hash ve salt kontrolü yap
                user_data = existing[0]
                stored_hash = user_data.get("password_hash")
                stored_salt = user_data.get("salt")
                
                # Hash ve salt eksikse ekle
                if not stored_hash or not stored_salt:
                    password_hash, salt = self._hash_password(password)
                    self.users_table.update(
                        {"password_hash": password_hash, "salt": salt},
                        self.Query.username == normalized_username
                    )
                else:
                    # Hash ve salt var, format kontrolü yap
                    # Mevcut hash'i doğrula - eğer doğrulama başarısızsa yeniden oluştur
                    password_valid = False
                    try:
                        password_valid = self.verify_password(username, password)
                    except Exception:
                        # Doğrulama hatası → hash formatı yanlış
                        password_valid = False
                    
                    if not password_valid:
                        # Hash formatı yanlış veya doğrulama başarısız → yeniden oluştur
                        password_hash, salt = self._hash_password(password)
                        self.users_table.update(
                            {
                                "password_hash": password_hash,
                                "salt": salt,
                                "updated_at": datetime.now().isoformat()
                            },
                            self.Query.username == normalized_username
                        )
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """
        Şifreyi güvenli bir şekilde hash'ler (public method)
        
        Args:
            password: Hash'lenecek şifre
            salt: Opsiyonel salt (yoksa otomatik oluşturulur)
            
        Returns:
            (hashed_password, salt) tuple'ı
        """
        return self._hash_password(password, salt)
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """
        Şifreyi güvenli bir şekilde hash'ler
        
        Args:
            password: Hash'lenecek şifre
            salt: Opsiyonel salt (hex string veya None)
            
        Returns:
            (hashed_password, salt_hex) tuple'ı
        """
        if salt is None:
            # Yeni salt oluştur (bytes olarak, sonra hex'e çevir)
            salt_bytes = secrets.token_bytes(16)
            salt_hex = salt_bytes.hex()
        else:
            # Salt hex string ise bytes'a çevir
            if isinstance(salt, str):
                salt_bytes = binascii.unhexlify(salt)
                salt_hex = salt
            else:
                # Zaten bytes ise
                salt_bytes = salt
                salt_hex = salt.hex()
        
        # PBKDF2-HMAC-SHA256 ile hash'le (100,000 iterasyon)
        # ÖNEMLİ: salt_bytes kullan (bytes olarak)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,  # ✅ Bytes kullan
            100000  # Güvenlik için yüksek iterasyon sayısı
        )
        
        # Hex formatına çevir
        hashed_password = password_hash.hex()
        
        return hashed_password, salt_hex
    
    def create_user(self, username: str, password: str, **kwargs) -> bool:
        """
        Yeni kullanıcı oluşturur
        
        Args:
            username: Kullanıcı adı
            password: Şifre (hash'lenecek)
            **kwargs: Ek bilgiler (email, role, vb.)
            
        Returns:
            Başarılıysa True, kullanıcı zaten varsa False
        """
        # Username'i normalize et
        normalized_username = self.normalize_username(username)
        if not normalized_username:
            return False
        
        # Normalize edilmiş username ile kontrol et
        existing = self.users_table.search(self.Query.username == normalized_username)
        if existing:
            return False
        
        # Şifreyi hash'le
        password_hash, salt = self._hash_password(password)
        
        # Kullanıcı oluştur (normalize edilmiş username ile kaydet)
        user_data = {
            "username": normalized_username,  # Normalize edilmiş username'i kaydet
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True,
            **kwargs
        }
        
        self.users_table.insert(user_data)
        return True
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        Kullanıcı bilgilerini getirir (case-insensitive ve strip ile)
        
        Args:
            username: Kullanıcı adı
            
        Returns:
            Kullanıcı bilgileri dictionary'si veya None
        """
        # Username'i normalize et (standart fonksiyon kullan)
        normalized_username = self.normalize_username(username)
        if not normalized_username:
            return None
        
        # TinyDB'de exact match ile ara (normalize edilmiş username ile)
        result = self.users_table.search(self.Query.username == normalized_username)
        if result:
            return result[0]
        
        # Case-insensitive arama için tüm kullanıcıları kontrol et
        all_users = self.users_table.all()
        for user in all_users:
            db_username = user.get("username", "").strip()
            normalized_db_username = self.normalize_username(db_username)
            if normalized_db_username == normalized_username:
                return user
        
        return None
    
    def verify_password(self, username: str, password: str) -> bool:
        """
        Kullanıcı şifresini doğrular
        
        Args:
            username: Kullanıcı adı
            password: Doğrulanacak şifre
            
        Returns:
            Şifre doğruysa True, değilse False
        """
        # Username'i normalize et (standart fonksiyon kullan)
        normalized_username = self.normalize_username(username)
        if not normalized_username:
            return False
        
        if not password:
            return False
        
        user = self.get_user(normalized_username)
        if not user:
            return False
        
        stored_hash = user.get("password_hash")
        salt_hex = user.get("salt")
        
        if not stored_hash or not salt_hex:
            return False
        
        # Şifreyi hash'le ve karşılaştır
        try:
            # Salt hex string'i bytes'a çevir
            salt_bytes = binascii.unhexlify(salt_hex)
            
            # PBKDF2-HMAC-SHA256 ile hash'le (bytes salt kullan)
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt_bytes,  # ✅ Bytes kullan
                100000
            )
            
            hashed_input = password_hash.hex()
            
            # Güvenli karşılaştırma (timing attack'a karşı)
            result = secrets.compare_digest(hashed_input, stored_hash)
            return result
        except Exception as e:
            return False
    
    def update_password(self, username: str, new_password: str) -> bool:
        """
        Kullanıcı şifresini günceller
        
        Args:
            username: Kullanıcı adı
            new_password: Yeni şifre
            
        Returns:
            Başarılıysa True, kullanıcı bulunamadıysa False
        """
        normalized_username = self.normalize_username(username)
        user = self.get_user(normalized_username)
        if not user:
            return False
        
        # Yeni şifreyi hash'le
        password_hash, salt = self._hash_password(new_password)
        
        # Güncelle (normalize edilmiş username ile)
        self.users_table.update(
            {
                "password_hash": password_hash,
                "salt": salt,
                "updated_at": datetime.now().isoformat()
            },
            self.Query.username == normalized_username
        )
        
        return True
    
    def delete_user(self, username: str) -> bool:
        """
        Kullanıcıyı siler
        
        Args:
            username: Kullanıcı adı
            
        Returns:
            Başarılıysa True, kullanıcı bulunamadıysa False
        """
        normalized_username = self.normalize_username(username)
        result = self.users_table.remove(self.Query.username == normalized_username)
        return len(result) > 0
    
    def list_users(self) -> List[Dict]:
        """
        Tüm kullanıcıları listeler
        
        Returns:
            Kullanıcı listesi (şifreler hariç)
        """
        users = self.users_table.all()
        # Şifre bilgilerini çıkar
        return [
            {
                "username": u.get("username"),
                "created_at": u.get("created_at"),
                "updated_at": u.get("updated_at"),
                "is_active": u.get("is_active", True)
            }
            for u in users
        ]
    
    def user_exists(self, username: str) -> bool:
        """
        Kullanıcı var mı kontrol eder (case-insensitive ve strip ile)
        
        Args:
            username: Kullanıcı adı
            
        Returns:
            Varsa True, yoksa False
        """
        return self.get_user(username) is not None

# Global user manager instance
user_manager = UserManager()

