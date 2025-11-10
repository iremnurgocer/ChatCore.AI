# -*- coding: utf-8 -*-
"""
ChatCore.AI - Kurumsal AI Chat Frontend Uygulaması

Bu modül Streamlit kullanarak kullanıcı dostu bir web arayüzü sağlar.
ChatGPT benzeri conversation yönetimi, oturum kontrolü ve güvenli authentication içerir.

Ne İşe Yarar:
- Web arayüzü sağlama (Streamlit ile)
- Kullanıcı login/logout işlemleri
- ChatGPT benzeri conversation yönetimi
- URL bazlı conversation ID yönetimi
- Gerçek zamanlı chat arayüzü
- Sidebar ile geçmiş sohbet yönetimi
- Backend API ile iletişim

Kullanım:
- Frontend'i başlatmak için: streamlit run app.py
- Tarayıcıda: http://localhost:8501
- Giriş: admin / 1234

Özellikler:
- JWT tabanlı kimlik doğrulama
- ChatGPT benzeri conversation yönetimi
- URL bazlı conversation ID yönetimi
- Gerçek zamanlı chat arayüzü
- Sidebar ile geçmiş sohbet yönetimi
"""

import os
import json
import requests
import streamlit as st
import time
from datetime import datetime

# CSS stil dosyasını yükle
try:
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'styles.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass  # CSS dosyası yoksa devam et
except Exception:
    pass  # CSS yükleme hatası durumunda devam et

# Yapılandırma Değişkenleri
# Backend API URL'i - environment değişkeninden alınır veya varsayılan değer kullanılır
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

# Şirket adı - environment değişkeninden alınır veya varsayılan değer kullanılır
COMPANY_NAME = os.getenv("COMPANY_NAME", "Company1")

# Streamlit sayfa yapılandırması
# layout="wide": Geniş ekran düzeni kullan
# initial_sidebar_state="expanded": Sidebar varsayılan olarak açık
# menu_items=None: Menü öğelerini gizle (URL değişikliğini önlemek için)
st.set_page_config(
    page_title=f"{COMPANY_NAME} AI Chat",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ============================================================================
# API İŞLEMLERİ - Backend ile iletişim fonksiyonları
# ============================================================================

def api_logout(token: str) -> bool:
    """
    Backend API'ye çıkış yapar ve kullanıcı oturumunu sonlandırır.
    
    Args:
        token: JWT authentication token
        
    Returns:
        bool: İşlem başarılıysa True, aksi halde False
    """
    url = f"{BACKEND_URL}/api/logout"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def api_login(username: str, password: str) -> tuple:
    """
    Backend API'ye kullanıcı girişi yapar ve JWT token alır.
    
    Args:
        username: Kullanıcı adı
        password: Kullanıcı şifresi
        
    Returns:
        tuple: (token, error_message) - Başarılıysa token döner, hata varsa error_message döner
    """
    url = f"{BACKEND_URL}/api/login"
    
    try:
        # Login isteği için payload hazırla
        payload = {"username": username, "password": password}
        
        # POST isteği gönder
        r = requests.post(url, json=payload, timeout=15)
        
        # Başarılı yanıt kontrolü
        if r.status_code == 200:
            data = r.json()
            # Backend 'access_token' döndürüyor, 'token' değil
            token = data.get("access_token") or data.get("token")
            if not token:
                return None, "Backend'den token alınamadı. Yanıt: " + str(data)
            return token, None
        
        # Hata durumunda detay bilgisini al
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        
        return None, f"Giriş başarısız ({r.status_code}): {detail}"
        
    except requests.exceptions.ConnectionError:
        # Backend'e bağlanılamıyor
        return None, f"Backend'e bağlanılamıyor. Backend'in çalıştığından emin olun: {BACKEND_URL}\nLütfen 'baslat.bat' dosyasını çalıştırın veya backend penceresinin açık olduğunu kontrol edin."
    
    except requests.exceptions.Timeout:
        # İstek zaman aşımına uğradı
        return None, "Backend yanıt vermiyor (timeout). Backend'in çalıştığından emin olun."
    
    except requests.RequestException as e:
        # Diğer HTTP hataları
        return None, f"Bağlantı hatası: {e}"
    
    except Exception as e:
        # Beklenmeyen hatalar
        return None, f"Hata: {str(e)}"

def api_chat(prompt: str, token: str, conversation_id: str = None):
    """
    Backend API'ye chat mesajı gönderir ve AI yanıtını alır.
    ChatGPT benzeri conversation yönetimi ile her mesaj bir conversation'a bağlıdır.
    
    Args:
        prompt: Kullanıcı mesajı
        token: JWT authentication token
        conversation_id: Mevcut conversation ID (opsiyonel, yeni conversation oluşturulabilir)
        
    Returns:
        tuple: ((response, conversation_id), error_message) - Başarılıysa yanıt ve conversation ID döner
    """
    url = f"{BACKEND_URL}/api/chat"
    try:
        payload = {"prompt": prompt}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=90,
        )
        if r.status_code == 200:
            data = r.json()
            response = data.get("response")
            conv_id = data.get("conversation_id")
            return (response, conv_id), None
        try:
            detail = r.json().get("detail") or r.json().get("error")
        except Exception:
            detail = r.text
        return None, f"API hatası ({r.status_code}): {detail}"
    except requests.exceptions.ConnectionError:
        return None, f"Backend'e bağlanılamıyor. Backend'in çalıştığından emin olun: {BACKEND_URL}"
    except requests.exceptions.Timeout:
        return None, "Backend yanıt vermiyor (timeout)"
    except requests.RequestException as e:
        return None, f"Ağ hatası: {e}"

def api_status():
    """Backend durumunu kontrol eder"""
    url = f"{BACKEND_URL}/api/status"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json(), None
        return None, "Backend kullanılamıyor"
    except requests.exceptions.ConnectionError as e:
        return None, f"Backend'e bağlanılamıyor. Backend'in çalıştığından emin olun: {BACKEND_URL}"
    except requests.exceptions.Timeout:
        return None, "Backend yanıt vermiyor (timeout)"
    except Exception as e:
        return None, f"Bağlantı hatası: {str(e)}"

def api_get_new_procedures(token: str, days: int = 30):
    """Yeni prosedürleri getirir"""
    url = f"{BACKEND_URL}/api/procedures/new"
    try:
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params={"days": days},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("new_procedures", []), None
        return [], f"API hatası ({r.status_code})"
    except Exception as e:
        return [], f"Hata: {str(e)}"

def api_mark_procedure_viewed(token: str, procedure_id: int):
    """Prosedürü görüntülendi olarak işaretle"""
    url = f"{BACKEND_URL}/api/procedures/{procedure_id}/mark-viewed"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False

def verify_token(token: str):
    """Token geçerliliğini kontrol eder - Sadece 401 durumunda False döner"""
    # Token gerektiren bir endpoint'i test et
    url = f"{BACKEND_URL}/api/status"
    try:
        r = requests.get(url, timeout=2)
        # Status endpoint herkese açık, backend çalışıyor mu kontrol eder
        if r.status_code == 200:
            # Backend çalışıyor, token'ı test et
            url2 = f"{BACKEND_URL}/api/employees"
            r2 = requests.get(
                url2,
                headers={"Authorization": f"Bearer {token}"},
                timeout=2
            )
            if r2.status_code == 200:
                return True
            elif r2.status_code == 401:
                return False
            # Diğer durumlarda token'ı geçerli kabul et
            return True
        # Backend çalışmıyor ama token'ı geçerli kabul et (sayfa yenileme sırasında)
        return True
    except:
        # Hata durumunda token'ı geçerli kabul et (backend henüz hazır olmayabilir)
        return True

def ensure_state():
    """Session state'i başlatır ve token doğrular"""
    # İlk yükleme için varsayılan değerler
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "current_conversation_id" not in st.session_state:
        st.session_state["current_conversation_id"] = None
    if "token_verified" not in st.session_state:
        st.session_state["token_verified"] = False
    if "token_check_time" not in st.session_state:
        st.session_state["token_check_time"] = None
    if "conversations_synced" not in st.session_state:
        st.session_state["conversations_synced"] = False
    if "conversation_list" not in st.session_state:
        st.session_state["conversation_list"] = []
    if "backend_active_conversation_id" not in st.session_state:
        st.session_state["backend_active_conversation_id"] = None
    if "initial_messages_loaded" not in st.session_state:
        st.session_state["initial_messages_loaded"] = False
    if "pending_new_chat" not in st.session_state:
        st.session_state["pending_new_chat"] = False

    # Token varsa ve username varsa, token'ı geçerli kabul et (sayfa yenileme durumunda)
    # Sadece açıkça geçersizse (401 dönerse) temizle
    if st.session_state.get("token") and st.session_state.get("username"):
        # Token ve username varsa, token_verified'i mutlaka True yap
        # Sayfa yenileme durumunda token'ı geçerli kabul et
        if not st.session_state.get("token_verified"):
            # Hızlı kontrol yap ama hata olursa token'ı geçerli kabul et
            try:
                token_valid = verify_token(st.session_state["token"])
                if token_valid is False:
                    # Token gerçekten geçersizse temizle
                    st.session_state["token"] = None
                    st.session_state["username"] = None
                    st.session_state["messages"] = []
                    st.session_state["current_conversation_id"] = None
                    st.session_state["token_verified"] = False
                else:
                    # Token geçerli veya kontrol edilemedi
                    st.session_state["token_verified"] = True
                    st.session_state["token_check_time"] = time.time()
            except Exception:
                # Hata durumunda token'ı geçerli kabul et (backend henüz hazır olmayabilir)
                st.session_state["token_verified"] = True
                st.session_state["token_check_time"] = time.time()
        else:
            # Token zaten doğrulanmış, token_verified'i True olarak koru
            st.session_state["token_verified"] = True

def add_message(role, content):
    """Geçmişe mesaj ekler"""
    st.session_state["messages"].append({"role": role, "content": content})

def switch_conversation(conv_id: str):
    """
    Conversation'ı değiştir ve mesajlarını yükle
    
    ChatGPT gibi conversation'lar arasında geçiş yapar.
    Her conversation kullanıcıya özeldir ve izole edilmiştir.
    Boş conversation'ları otomatik temizler.
    """
    if not conv_id:
        st.error("Geçersiz sohbet ID'si")
        return
    
    # Sync flag'lerini temizle (yeni conversation için sync yapılabilir)
    for key in list(st.session_state.keys()):
        if key.startswith("sync_conversation_"):
            del st.session_state[key]
    
    # Önceki boş conversation'ı temizle (sadece gerçekten boşsa - message_count == 0)
    current_conv_id = st.session_state.get("current_conversation_id")
    current_messages = st.session_state.get("messages", [])
    
    # Sadece frontend'de mesaj yoksa VE backend'de de mesaj yoksa sil
    if current_conv_id and len(current_messages) == 0:
        # Backend'den conversation bilgisini kontrol et
        try:
            convs_r = requests.get(
                f"{BACKEND_URL}/api/conversations",
                headers={"Authorization": f"Bearer {st.session_state['token']}"},
                timeout=5
            )
            if convs_r.status_code == 200:
                convs_data = convs_r.json()
                conversations = convs_data.get("conversations", [])
                for conv in conversations:
                    if conv.get("conversation_id") == current_conv_id:
                        # Mesaj sayısı 0 ise sil
                        if conv.get("message_count", 0) == 0:
                            try:
                                requests.delete(
                                    f"{BACKEND_URL}/api/conversations/{current_conv_id}",
                                    headers={"Authorization": f"Bearer {st.session_state['token']}"},
                                    timeout=5
                                )
                            except:
                                pass
                        break
        except:
            pass  # Kontrol başarısız olsa bile devam et
    
    try:
        # Conversation'ı aktif yap
        r = requests.post(
            f"{BACKEND_URL}/api/conversations/{conv_id}/switch",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10
        )
        
        if r.status_code == 200:
            st.session_state["current_conversation_id"] = conv_id
            st.session_state["backend_active_conversation_id"] = conv_id
            st.session_state["initial_messages_loaded"] = True
            st.session_state["pending_new_chat"] = False
            set_conversation_id_in_url(conv_id)
            
            # Yeni conversation'ın mesajlarını yükle
            try:
                r2 = requests.get(
                    f"{BACKEND_URL}/api/conversation/{conv_id}/restore",
                    headers={"Authorization": f"Bearer {st.session_state['token']}"},
                    timeout=10
                )
                if r2.status_code == 200:
                    data2 = r2.json()
                    messages = data2.get("messages", [])
                    st.session_state["messages"] = []
                    for msg in messages:
                        st.session_state["messages"].append({
                            "role": msg.get("role"),
                            "content": msg.get("content")
                        })
            except Exception as e:
                # Mesajlar yüklenemedi ama conversation değişti
                st.session_state["messages"] = []
            
            # Cache içindeki aktif işaretini güncelle (sıralamayı değiştirmeden)
            cached_list = st.session_state.get("conversation_list", [])
            for cached in cached_list:
                cid = cached.get("conversation_id") or cached.get("id")
                cached["is_active"] = cid == conv_id
            st.session_state["conversation_list"] = cached_list
            
            st.rerun()
        elif r.status_code == 404:
            st.error("Sohbet bulunamadı. Lütfen sayfayı yenileyin.")
        elif r.status_code == 403:
            st.error("Bu sohbete erişim yetkiniz yok.")
        else:
            # Conversation değiştirilemedi
            try:
                error_detail = r.json().get("detail") or r.json().get("error", "Bilinmeyen hata")
                st.error(f"Sohbet değiştirilemedi: {error_detail}")
            except:
                st.error(f"Sohbet değiştirilemedi (HTTP {r.status_code})")
    except requests.exceptions.Timeout:
        st.error("Bağlantı zaman aşımına uğradı. Lütfen tekrar deneyin.")
    except requests.exceptions.ConnectionError:
        st.error("Backend'e bağlanılamıyor. Backend'in çalıştığından emin olun.")
    except requests.exceptions.RequestException as e:
        st.error(f"Bağlantı hatası: {str(e)}")
    except Exception as e:
        st.error(f"Sohbet değiştirilemedi: {str(e)}")


def delete_conversation(conv_id: str):
    """Delete a conversation and refresh the sidebar list."""
    if not st.session_state.get("token"):
        st.error("Please log in to manage chats.")
        return

    try:
        r = requests.delete(
            f"{BACKEND_URL}/api/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10
        )

        if r.status_code == 200:
            if st.session_state.get("current_conversation_id") == conv_id:
                st.session_state["current_conversation_id"] = None
                st.session_state["messages"] = []
                st.session_state["initial_messages_loaded"] = False
                st.session_state["pending_new_chat"] = False
                clear_conversation_id_from_url()

            st.session_state["conversations_synced"] = False
            st.success("Conversation deleted.")
            st.rerun()
        elif r.status_code == 404:
            st.warning("Conversation not found.")
        elif r.status_code == 403:
            st.error("You do not have permission to delete this conversation.")
        else:
            try:
                detail = r.json().get("detail") or r.json().get("error", "")
            except Exception:
                detail = ""
            extra = f" ({detail})" if detail else ""
            st.error(f"Conversation could not be deleted: HTTP {r.status_code}{extra}")
    except requests.exceptions.Timeout:
        st.error("Delete request timed out.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the backend. Please check the server status.")
    except requests.exceptions.RequestException as e:
        st.error(f"Delete request failed: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error while deleting: {str(e)}")


def fetch_conversation_list(force: bool = False):
    """Fetch and cache the conversation list from the backend."""
    if not st.session_state.get("token"):
        return st.session_state.get("conversation_list", [])

    if not force and st.session_state.get("conversations_synced") and st.session_state.get("conversation_list"):
        return st.session_state.get("conversation_list")

    try:
        r = requests.get(
            f"{BACKEND_URL}/api/conversations",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            st.session_state["conversation_list"] = data.get("conversations", [])
            st.session_state["backend_active_conversation_id"] = data.get("active_conversation_id")
            st.session_state["conversations_synced"] = True
        else:
            st.session_state["conversation_list"] = st.session_state.get("conversation_list", [])
    except requests.exceptions.RequestException:
        pass
    except Exception:
        pass

    return st.session_state.get("conversation_list", [])


# Prosedür bildirim kontrolü
def check_new_procedures():
    """Yeni prosedürleri kontrol et ve bildirim göster"""
    if not st.session_state.get("token"):
        return
    
    # Sadece belirli aralıklarla kontrol et (her sayfa yüklemesinde değil)
    import time
    current_time = time.time()
    last_check = st.session_state.get("procedure_check_time", 0)
    
    # Son kontrol 5 dakikadan eskiyse veya ilk kontrol ise
    if current_time - last_check > 300 or last_check == 0:
        new_procedures, err = api_get_new_procedures(st.session_state["token"], days=30)
        
        if new_procedures:
            st.session_state["new_procedures_notification"] = new_procedures
        else:
            st.session_state["new_procedures_notification"] = []
        
        st.session_state["procedure_check_time"] = current_time

# URL parametrelerini yönet (ChatGPT benzeri conversation ID yönetimi)
def get_conversation_id_from_url():
    """URL'den conversation ID'yi al"""
    try:
        # Streamlit 1.28+ için query_params
        if hasattr(st, 'query_params'):
            chat_id = st.query_params.get("chat")
            if chat_id:
                # List olarak dönerse ilk elemanı al
                if isinstance(chat_id, list):
                    return chat_id[0] if chat_id else None
                return str(chat_id)
    except:
        pass
    return None

def clear_conversation_id_from_url():
    """URL'den conversation ID parametresini temizle"""
    try:
        if hasattr(st, 'query_params'):
            # Streamlit 1.28+ için
            if "chat" in st.query_params:
                # Parametreleri dict olarak al, chat'i çıkar
                params = dict(st.query_params)
                params.pop("chat", None)
                # Parametreleri güncelle
                if params:
                    st.query_params.update(params)
                else:
                    # Tüm parametreleri temizle
                    st.query_params.clear()
    except Exception as e:
        # Eski versiyonlar için experimental API
        try:
            if hasattr(st, 'experimental_set_query_params'):
                # Parametreleri temizle
                st.experimental_set_query_params()
        except:
            pass

def set_conversation_id_in_url(conversation_id: str):
    """URL'ye conversation ID ekle"""
    try:
        # Streamlit 1.28+ için
        if hasattr(st, 'query_params'):
            # Mevcut parametreleri koru
            params = dict(st.query_params)
            params["chat"] = conversation_id
            st.query_params.update(params)
    except:
        # Eski versiyonlar için experimental API
        try:
            if hasattr(st, 'experimental_set_query_params'):
                st.experimental_set_query_params(chat=conversation_id)
        except:
            pass

def restore_session_from_conversation(conversation_id: str):
    """Conversation ID'den session'ı restore et"""
    url = f"{BACKEND_URL}/api/conversation/{conversation_id}/restore"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("token"), data.get("user_id"), None
        return None, None, f"Session restore failed: {r.status_code}"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

def load_initial_conversation():
    """
    Aktif conversation'ı backend'den yükler ve mesaj geçmişini senkronize eder.
    Eski app.py davranışını koruyarak sayfa yenilemelerinde sıralama ve aktif sohbet
    durumunun doğru görünmesini sağlar.
    """
    if not st.session_state.get("token"):
        return

    conversations = fetch_conversation_list()

    if st.session_state.get("pending_new_chat"):
        return

    active_conv_id = st.session_state.get("current_conversation_id")
    if not active_conv_id:
        active_conv_id = st.session_state.get("backend_active_conversation_id")
        if active_conv_id:
            st.session_state["current_conversation_id"] = active_conv_id

    if not active_conv_id:
        return

    if st.session_state.get("messages"):
        return

    if st.session_state.get("initial_messages_loaded"):
        return

    try:
        r2 = requests.get(
            f"{BACKEND_URL}/api/conversation/{active_conv_id}/restore",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10
        )
        if r2.status_code == 200:
            data2 = r2.json()
            messages = data2.get("messages", [])
            st.session_state["messages"] = [
                {"role": msg.get("role"), "content": msg.get("content")}
                for msg in messages
            ]
    except Exception:
        pass

    st.session_state["initial_messages_loaded"] = True

# UI başlatma
import time
ensure_state()

# URL'den conversation ID oku
url_conversation_id = get_conversation_id_from_url()

# RESTORE İŞLEMİNİ TAMAMEN DEVRE DIŞI BIRAK
# Logout sonrası giriş ekranında restore işlemi çalışmamalı
# Restore sadece kullanıcı zaten giriş yapmışsa ve URL'de conversation ID varsa çalışmalı
# (Bu durumda restore değil, sadece conversation'a geçiş yapılır - aşağıda conversation yönetimi kısmında)

# Conversation yönetimi - URL'den veya backend'den conversation ID'yi al
# Sadece token ve token_verified True ise conversation yönetimi yap
if st.session_state.get("token") and st.session_state.get("token_verified"):
    # URL'den conversation ID varsa onu kullan
    if url_conversation_id:
        # URL'deki conversation ID'yi aktif yap
        if st.session_state.get("current_conversation_id") != url_conversation_id:
            try:
                # Conversation'ı aktif yap
                r = requests.post(
                    f"{BACKEND_URL}/api/conversations/{url_conversation_id}/switch",
                    headers={"Authorization": f"Bearer {st.session_state['token']}"},
                    timeout=10
                )
                if r.status_code == 200:
                    st.session_state["current_conversation_id"] = url_conversation_id
                    # Conversation mesajlarını yükle
                    r2 = requests.get(
                        f"{BACKEND_URL}/api/conversation/{url_conversation_id}/restore",
                        headers={"Authorization": f"Bearer {st.session_state['token']}"},
                        timeout=10
                    )
                    if r2.status_code == 200:
                        data2 = r2.json()
                        messages = data2.get("messages", [])
                        st.session_state["messages"] = []
                        for msg in messages:
                            st.session_state["messages"].append({
                                "role": msg.get("role"),
                                "content": msg.get("content")
                            })
            except:
                pass

    load_initial_conversation()

# Yeni prosedür bildirimi kontrolü (giriş yapılmışsa)
if st.session_state.get("token"):
    check_new_procedures()

# Başlık
st.markdown(
    f"""
    <div style="text-align:center; margin-top:1rem; margin-bottom:0.5rem;">
      <h1 style="margin-bottom:0.2rem;">{COMPANY_NAME} AI Asistanı</h1>
      <p style="opacity:0.7; margin-top:0;">Kurumsal AI destekli chat sistemi</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Örnek Sorular (sadece mesaj yoksa göster)
example_questions = [
    "Enerji departmanında kimler çalışıyor?",
    "Hangi projeler devam ediyor?",
    "Ahmet Yılmaz'ın projeleri neler?",
    "Turizm departmanının bütçesi nedir?",
    "Bodrum'da hangi projeler var?"
]

# Mesaj yoksa örnek soruları göster
if len(st.session_state.get("messages", [])) == 0 and st.session_state.get("token"):
    st.markdown("### Örnek Sorular")
    st.markdown("Hızlıca başlamak için aşağıdaki örnek sorulardan birini seçebilirsiniz:")
    
    # Örnek soruları 2 sütunda göster
    col1, col2 = st.columns(2)
    for idx, q in enumerate(example_questions):
        with col1 if idx % 2 == 0 else col2:
            if st.button(q, key=f"example_{idx}", use_container_width=True):
                st.session_state["example_question"] = q
                st.rerun()
    st.markdown("---")

# Giriş Ekranı - Sadece token yoksa veya açıkça geçersizse göster
# Token varsa ve token_verified False ise, ensure_state zaten kontrol etti ve True yaptı
# Burada sadece gerçekten token yoksa veya açıkça geçersizse giriş ekranını göster
if not st.session_state.get("token"):
    # Token yoksa giriş ekranını göster
    # Giriş ekranına girildiğinde URL'de conversation ID varsa temizle
    if url_conversation_id:
        clear_conversation_id_from_url()
    
    # Token yoksa, session state'i temizle (logout sonrası veya ilk giriş)
    # Sadece giriş ekranına özgü değerleri temizle, diğerlerini koru
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "current_conversation_id" not in st.session_state:
        st.session_state["current_conversation_id"] = None
    if "token_verified" not in st.session_state:
        st.session_state["token_verified"] = False
    
    # Giriş ekranını göster
    with st.container():
        st.subheader("Giriş", divider="gray")
        col1, col2 = st.columns([1, 1])
        with col1:
            username = st.text_input(
                "Kullanıcı Adı",
                value=st.session_state.get("username") or "",
                placeholder="admin",
                key="login_username"
            )
        with col2:
            password = st.text_input(
                "Şifre",
                type="password",
                value="",
                placeholder="******",
                key="login_password"
            )

        login_btn = st.button("Giriş Yap", type="primary", use_container_width=True)
        if login_btn:
            token, err = api_login(username.strip(), password)
            if token:
                current_username = username.strip()
                
                st.session_state["token"] = token
                st.session_state["username"] = current_username
                st.session_state["token_verified"] = True
                st.session_state["token_check_time"] = time.time()
                st.session_state["messages"] = []
                st.session_state["current_conversation_id"] = None  # Mesaj gönderilene kadar None
                st.session_state["conversations_synced"] = False
                st.session_state["conversation_list"] = []
                st.session_state["backend_active_conversation_id"] = None
                st.session_state["initial_messages_loaded"] = False
                st.session_state["pending_new_chat"] = False
                
                # Yeni conversation oluşturma - sadece ilk mesaj gönderildiğinde oluşturulacak
                # URL'yi temizle
                clear_conversation_id_from_url()
                
                st.rerun()
            else:
                st.error(err or "Geçersiz kullanıcı adı veya şifre.")

    # Backend durumu
    status, status_err = api_status()
    if status:
        employees = status.get('data_sources', {}).get('employees', 0)
        projects = status.get('data_sources', {}).get('projects', 0)
        st.info(f"Backend aktif - {employees} çalışan, {projects} proje")
    else:
        st.warning(f"{status_err}")
    
    st.caption(f"Backend URL: `{BACKEND_URL}`")
    st.stop()

# Chat Ekranı
# Sidebar
with st.sidebar:
    st.markdown("### Kullanıcı")
    st.write(f"**{st.session_state['username']}**")

    if st.button("Çıkış Yap", use_container_width=True):
        # Backend'e logout isteği gönder
        if st.session_state.get("token"):
            try:
                api_logout(st.session_state["token"])
            except:
                pass
        
        # URL'den conversation ID parametresini önce temizle
        clear_conversation_id_from_url()
        
        # Tüm session state'i temizle
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        
        # Sayfayı yenile - giriş ekranına dön (URL parametresi olmadan)
        st.rerun()
    
    st.divider()
    
    # Yeni Sohbet butonu
    if st.button("Yeni Sohbet", use_container_width=True, type="primary"):
        st.session_state["messages"] = []
        st.session_state["current_conversation_id"] = None
        st.session_state["initial_messages_loaded"] = False
        st.session_state["backend_active_conversation_id"] = None
        st.session_state["pending_new_chat"] = True
        
        cached_list = st.session_state.get("conversation_list", [])
        for cached in cached_list:
            cached["is_active"] = False
        st.session_state["conversation_list"] = cached_list
        
        clear_conversation_id_from_url()
        st.rerun()
    
    st.divider()
    
    # Geçmiş Sohbetler
    st.markdown("### Geçmiş Sohbetler")

    conversations = fetch_conversation_list()
    backend_active_conv_id = st.session_state.get("backend_active_conversation_id")

    if backend_active_conv_id and not st.session_state.get("current_conversation_id") and not st.session_state.get("pending_new_chat"):
        st.session_state["current_conversation_id"] = backend_active_conv_id
        set_conversation_id_in_url(backend_active_conv_id)

    if conversations:
        delete_icon = "\U0001F5D1"
        for conv in conversations[:10]:
            conv_id = conv.get("conversation_id") or conv.get("id")
            title = conv.get("title", "Basliksiz")
            msg_count = conv.get("message_count", 0)

            display_title = title[:50] + "..." if len(title) > 50 else title
            label = f"{display_title} ({msg_count})"

            button_kwargs = {"use_container_width": True}
            if conv_id and conv_id == st.session_state.get("current_conversation_id"):
                button_kwargs["type"] = "primary"

            row_cols = st.columns([0.8, 0.2])
            if row_cols[0].button(label, key=f"conv_{conv_id}", **button_kwargs):
                switch_conversation(conv_id)

            if row_cols[1].button(delete_icon, key=f"conv_delete_{conv_id}", use_container_width=True, help="Sohbeti sil"):
                delete_conversation(conv_id)
    else:
        st.caption("Henuz sohbet yok")

    st.divider()
    
    # Yeni prosedür bildirimi
    new_procedures = st.session_state.get("new_procedures_notification", [])
    if new_procedures:
        st.markdown("### Yeni Prosedürler")
        for proc in new_procedures[:5]:  # İlk 5 tanesini göster
            with st.container():
                proc_id = proc.get("id")
                title = proc.get("title", "Başlıksız")
                days = proc.get("days_since_published", 0)
                priority = proc.get("priority", "Orta")
                
                # Önceliğe göre etiket
                priority_labels = {
                    "Kritik": "[KRITIK]",
                    "Yüksek": "[YUKSEK]",
                    "Orta": "[ORTA]",
                    "Düşük": "[DUSUK]"
                }
                priority_label = priority_labels.get(priority, "[ORTA]")
                
                st.markdown(f"{priority_label} **{title}**")
                st.caption(f"{days} gün önce yayınlandı")
                
                if st.button("Görüntüle", key=f"view_proc_{proc_id}", use_container_width=True):
                    # Prosedürü görüntülendi olarak işaretle
                    api_mark_procedure_viewed(st.session_state["token"], proc_id)
                    # Bildirimden kaldır
                    st.session_state["new_procedures_notification"] = [
                        p for p in new_procedures if p.get("id") != proc_id
                    ]
                    
                    # Chat'e prosedür bilgisini ekle
                    proc_text = f"Prosedür: {title}\nKod: {proc.get('code', 'N/A')}\nDepartman: {proc.get('department', 'N/A')}\nKategori: {proc.get('category', 'N/A')}\nİçerik: {proc.get('content', 'N/A')}"
                    st.session_state["example_question"] = f"'{title}' prosedürü hakkında bilgi ver"
                    st.rerun()
                
                st.divider()
        
        if len(new_procedures) > 5:
            st.caption(f"... ve {len(new_procedures) - 5} prosedür daha")
    
    st.divider()
    st.caption(f"Backend: `{BACKEND_URL}`")

# Mesaj geçmişi
for m in st.session_state["messages"]:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# Örnek soruyu işle
if "example_question" in st.session_state:
    user_prompt = st.session_state.pop("example_question")
    # Örnek soruyu doğrudan işle
    add_message("user", user_prompt)
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Yanıt oluşturuluyor..."):
            conv_id = st.session_state.get("current_conversation_id")
            result, err = api_chat(user_prompt, st.session_state["token"], conv_id)
            if err:
                st.error(f"{err}")
                add_message("assistant", f"Hata: {err}")
            else:
                response, new_conv_id = result
                st.markdown(response or "")
                add_message("assistant", response or "")
                st.session_state["conversations_synced"] = False
                st.session_state["pending_new_chat"] = False
                
                # Conversation ID'yi güncelle (yeni oluşturulduysa veya ilk mesaj gönderildiyse)
                if new_conv_id:
                    st.session_state["current_conversation_id"] = new_conv_id
                    st.session_state["backend_active_conversation_id"] = new_conv_id
                    set_conversation_id_in_url(new_conv_id)
                else:
                    st.session_state["backend_active_conversation_id"] = st.session_state.get("current_conversation_id")
    
    st.rerun()

# Chat input - her zaman en altta görünür olmalı
# Sabit key kullanarak URL değişikliğini minimize et
user_prompt = st.chat_input("Mesajınızı yazın...", key="main_chat_input")

# Kullanıcı mesajını işle
if user_prompt:
    # GÜVENLİK: Token kontrolü - giriş yapmadan soru sorulamaz
    if not st.session_state.get("token") or not st.session_state.get("token_verified"):
        st.error("Giriş yapmadan soru soramazsınız. Lütfen giriş yapın.")
        st.stop()
    
    # Mesajı session state'e ekle (geçici olarak, API yanıt gelene kadar)
    add_message("user", user_prompt)
    
    # Kullanıcı mesajını göster
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Asistan yanıtını göster
    with st.chat_message("assistant"):
        with st.spinner("Yanıt oluşturuluyor..."):
            conv_id = st.session_state.get("current_conversation_id")
            result, err = api_chat(user_prompt, st.session_state["token"], conv_id)
            
            if err:
                st.error(f"{err}")
                # Hata durumunda kullanıcı mesajını geri al (yeniden eklenmemesi için)
                if st.session_state.get("messages") and st.session_state["messages"][-1]["role"] == "user":
                    st.session_state["messages"].pop()
                add_message("assistant", f"Hata: {err}")
            else:
                response, new_conv_id = result
                st.markdown(response or "")
                add_message("assistant", response or "")
                
                # Conversation ID'yi güncelle (yeni oluşturulduysa veya ilk mesaj gönderildiyse)
                if new_conv_id:
                    st.session_state["current_conversation_id"] = new_conv_id
                    set_conversation_id_in_url(new_conv_id)
    
    # Sayfayı yenile - örnek soruların kaybolması için
    st.rerun()

# Footer
st.divider()
st.caption(f"© {COMPANY_NAME} AI Chat Demo - Kurumsal İletişim Asistanı")
