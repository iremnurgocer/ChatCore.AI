"""
Streamlit Frontend - Kurumsal AI Chat Arayüzü
AI chat entegrasyonu için profesyonel ve sade UI
"""
import os
import json
import requests
import streamlit as st

# Yapılandırma
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Company1")

st.set_page_config(
    page_title=f"{COMPANY_NAME} AI Chat",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None  # Menü öğelerini devre dışı bırak (URL değişikliğini önler)
)

# Yardımcı Fonksiyonlar
def api_login(username: str, password: str):
    """Backend API'ye giriş yapar"""
    url = f"{BACKEND_URL}/api/login"
    try:
        r = requests.post(url, json={"username": username, "password": password}, timeout=15)
        if r.status_code == 200:
            return r.json().get("token"), None
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        return None, f"Giriş başarısız ({r.status_code}): {detail}"
    except requests.exceptions.ConnectionError:
        return None, f"Backend'e bağlanılamıyor. Backend'in çalıştığından emin olun: {BACKEND_URL}\nLütfen 'baslat.bat' dosyasını çalıştırın veya backend penceresinin açık olduğunu kontrol edin."
    except requests.exceptions.Timeout:
        return None, "Backend yanıt vermiyor (timeout). Backend'in çalıştığından emin olun."
    except requests.RequestException as e:
        return None, f"Bağlantı hatası: {e}"

def api_chat(prompt: str, token: str):
    """API'ye chat isteği gönderir"""
    url = f"{BACKEND_URL}/api/chat"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={"prompt": prompt},
            timeout=90,  # Gemini API için timeout artırıldı (çoklu model denemesi için)
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("response"), None
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
    url = f"{BACKEND_URL}/api/employees"
    try:
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=2  # Timeout'u kısalttık (sayfa yenileme hızlı olmalı)
        )
        # 200 dönerse token geçerli
        if r.status_code == 200:
            return True
        # SADECE 401 dönerse token geçersiz - diğer tüm durumlarda True döndür
        elif r.status_code == 401:
            return False
        # Diğer durumlarda (500, 404, vb.) token'ı geçerli kabul et (backend sorunu olabilir)
        # Sayfa yenileme sırasında backend henüz başlamamış olabilir
        return True
    except requests.exceptions.ConnectionError:
        # Backend'e bağlanılamıyorsa token'ı geçerli kabul et (backend çalışmıyor olabilir)
        # Sayfa yenileme sırasında backend henüz hazır olmayabilir
        return True
    except requests.exceptions.Timeout:
        # Timeout olursa token'ı geçerli kabul et (backend yavaş olabilir)
        return True
    except Exception:
        # Diğer tüm hatalarda token'ı geçerli kabul et (backend sorunu olabilir)
        # Sayfa yenileme sırasında backend henüz hazır olmayabilir
        return True

def ensure_state():
    """Session state'i başlatır ve token doğrular"""
    # İlk yükleme için varsayılan değerler - MEVCUT DEĞERLERİ KORU
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "token_verified" not in st.session_state:
        st.session_state["token_verified"] = False
    if "token_check_time" not in st.session_state:
        st.session_state["token_check_time"] = None
    
    # Token varsa kontrol et
    if st.session_state.get("token"):
        import time
        current_time = time.time()
        last_check = st.session_state.get("token_check_time")
        
        # Eğer token hiç doğrulanmamışsa ve zaman damgası yoksa, doğrula
        # Ama başarısız olursa bile token'ı SİLME (backend geçici olarak çalışmıyor olabilir)
        if st.session_state.get("token_verified") is False and last_check is None:
            # İlk kontrol - token'ı doğrula
            token_valid = verify_token(st.session_state["token"])
            if token_valid:
                st.session_state["token_verified"] = True
                st.session_state["token_check_time"] = current_time
            # Başarısız olsa bile token'ı koru (sayfa yenileme sırasında backend başlamamış olabilir)
            # Token sadece AÇIKÇA 401 döndüğünde silinecek (verify_token içinde False dönerse)
        
        # Token daha önce doğrulanmışsa ve 15 dakikadan fazla geçtiyse, tekrar kontrol et
        elif st.session_state.get("token_verified") is True and last_check and (current_time - last_check) > 900:
            # Periyodik kontrol - token daha önce doğrulanmışsa
            token_valid = verify_token(st.session_state["token"])
            # Sadece AÇIKÇA geçersizse (401) temizle
            if token_valid is False:
                # Token gerçekten geçersizse temizle (sadece 401 durumunda)
                st.session_state["token"] = None
                st.session_state["username"] = None
                st.session_state["messages"] = []
                st.session_state["token_verified"] = False
                st.session_state["token_check_time"] = None
            else:
                # Token geçerli veya belirsiz (backend sorunu), zamanı güncelle
                st.session_state["token_check_time"] = current_time
        
        # Token doğrulanmışsa ve süresi dolmamışsa hiçbir şey yapma

def add_message(role, content):
    """Geçmişe mesaj ekler"""
    st.session_state["messages"].append({"role": role, "content": content})

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

# URL parametrelerini temizle (sayfa yenileme sonrası session kaybını önler)
# Streamlit widget'ları URL'de query parametreleri oluşturabilir, bunları temizle
try:
    # Streamlit 1.28+ için
    if hasattr(st, 'query_params') and st.query_params:
        # Query parametrelerini temizle - URL'deki ?param=value gibi parametreleri kaldır
        st.experimental_set_query_params({}) if hasattr(st, 'experimental_set_query_params') else None
except:
    # Eski Streamlit versiyonları için
    pass

# UI
ensure_state()

# Conversation yönetimi - aktif conversation ID'yi backend'den al
if st.session_state.get("token") and "active_conversation_id" not in st.session_state:
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/conversations",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            st.session_state["active_conversation_id"] = data.get("active_conversation_id")
            # Aktif conversation'ın mesajlarını yükle
            convs = data.get("conversations", [])
            active_conv = next((c for c in convs if c.get("conversation_id") == st.session_state["active_conversation_id"]), None)
            if active_conv and active_conv.get("message_count", 0) > 0:
                # Mesajları backend'den al
                r2 = requests.get(
                    f"{BACKEND_URL}/api/sessions/{st.session_state['username']}",
                    headers={"Authorization": f"Bearer {st.session_state['token']}"},
                    timeout=10
                )
                if r2.status_code == 200:
                    data2 = r2.json()
                    messages = data2.get("messages", [])
                    # LLM formatını Streamlit formatına çevir
                    for msg in messages:
                        st.session_state["messages"].append({
                            "role": msg.get("role"),
                            "content": msg.get("content")
                        })
    except:
        pass  # İlk yükleme başarısız olursa devam et

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
    st.markdown("### 💡 Örnek Sorular")
    st.markdown("Hızlıca başlamak için aşağıdaki örnek sorulardan birini seçebilirsiniz:")
    
    # Örnek soruları 2 sütunda göster
    col1, col2 = st.columns(2)
    for idx, q in enumerate(example_questions):
        with col1 if idx % 2 == 0 else col2:
            if st.button(q, key=f"example_{idx}", use_container_width=True):
                st.session_state["example_question"] = q
                st.rerun()
    st.markdown("---")

# Giriş Ekranı
if not st.session_state["token"]:
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
                placeholder="????",
                key="login_password"
            )

        login_btn = st.button("Giriş Yap", type="primary", use_container_width=True)
        if login_btn:
            token, err = api_login(username.strip(), password)
            if token:
                import time
                # Eğer farklı bir kullanıcı adıyla giriş yapılıyorsa mesajları temizle
                previous_username = st.session_state.get("username")
                current_username = username.strip()
                
                st.session_state["token"] = token
                st.session_state["username"] = current_username
                st.session_state["token_verified"] = True
                st.session_state["token_check_time"] = time.time()
                
                # Sadece farklı kullanıcı adıyla giriş yapıldıysa mesajları temizle
                if previous_username and previous_username != current_username:
                    st.session_state["messages"] = []  # Farklı kullanıcı için mesajları temizle
                # Aynı kullanıcı adıyla giriş yapıldıysa mesajları koru
                
                st.success("Giriş başarılı, yönlendiriliyor...")
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
        # Tüm session state'i temizle
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    
    st.divider()
    
    # Yeni Sohbet butonu
    if st.button("➕ Yeni Sohbet", use_container_width=True, type="primary"):
        # Yeni conversation oluştur
        try:
            r = requests.post(
                f"{BACKEND_URL}/api/conversations/new",
                headers={"Authorization": f"Bearer {st.session_state['token']}"},
                timeout=10
            )
            if r.status_code == 200:
                st.session_state["messages"] = []  # Mesajları temizle
                st.success("Yeni sohbet başlatıldı!")
                st.rerun()
        except Exception as e:
            st.error(f"Sohbet oluşturulamadı: {e}")
    
    st.divider()
    
    # Geçmiş Sohbetler
    st.markdown("### 💬 Geçmiş Sohbetler")
    
    # Conversation'ları getir
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/conversations",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            conversations = data.get("conversations", [])
            active_conv_id = data.get("active_conversation_id")
            
            # Conversation listesi göster
            if conversations:
                for conv in conversations[:10]:  # İlk 10'u göster
                    conv_id = conv.get("conversation_id")
                    title = conv.get("title", "Başlıksız")
                    is_active = conv.get("is_active", False)
                    msg_count = conv.get("message_count", 0)
                    
                    # Aktif conversation'ı vurgula
                    if is_active:
                        label = f"🔵 {title} ({msg_count})"
                    else:
                        label = f"{title} ({msg_count})"
                    
                    # Conversation butonu
                    if st.button(label, key=f"conv_{conv_id}", use_container_width=True):
                        # Conversation'ı değiştir
                        try:
                            r = requests.post(
                                f"{BACKEND_URL}/api/conversations/{conv_id}/switch",
                                headers={"Authorization": f"Bearer {st.session_state['token']}"},
                                timeout=10
                            )
                            if r.status_code == 200:
                                # Yeni conversation'ın mesajlarını yükle
                                st.session_state["messages"] = []
                                # Mesajları backend'den al
                                r2 = requests.get(
                                    f"{BACKEND_URL}/api/sessions/{st.session_state['username']}",
                                    headers={"Authorization": f"Bearer {st.session_state['token']}"},
                                    timeout=10
                                )
                                if r2.status_code == 200:
                                    data = r2.json()
                                    messages = data.get("messages", [])
                                    # LLM formatını Streamlit formatına çevir
                                    for msg in messages:
                                        st.session_state["messages"].append({
                                            "role": msg.get("role"),
                                            "content": msg.get("content")
                                        })
                                st.rerun()
                        except:
                            st.error("Sohbet değiştirilemedi")
            else:
                st.caption("Henüz sohbet yok")
    except:
        st.caption("Sohbetler yüklenemedi")
    
    st.divider()
    
    # Yeni prosedür bildirimi
    new_procedures = st.session_state.get("new_procedures_notification", [])
    if new_procedures:
        st.markdown("### 🔔 Yeni Prosedürler")
        for proc in new_procedures[:5]:  # İlk 5 tanesini göster
            with st.container():
                proc_id = proc.get("id")
                title = proc.get("title", "Başlıksız")
                days = proc.get("days_since_published", 0)
                priority = proc.get("priority", "Orta")
                
                # Önceliğe göre renk
                priority_colors = {
                    "Kritik": "🔴",
                    "Yüksek": "🟠",
                    "Orta": "🟡",
                    "Düşük": "🟢"
                }
                priority_icon = priority_colors.get(priority, "⚪")
                
                st.markdown(f"{priority_icon} **{title}**")
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
            response, err = api_chat(user_prompt, st.session_state["token"])
            if err:
                st.error(f"{err}")
                add_message("assistant", f"Hata: {err}")
            else:
                st.markdown(response or "")
                add_message("assistant", response or "")
    
    st.rerun()

# Chat input - her zaman en altta görünür olmalı
# Sabit key kullanarak URL değişikliğini minimize et
user_prompt = st.chat_input("Mesajınızı yazın...", key="main_chat_input")

# Kullanıcı mesajını işle
if user_prompt:
    # Mesajı session state'e ekle
    add_message("user", user_prompt)
    
    # Kullanıcı mesajını göster
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Asistan yanıtını göster
    with st.chat_message("assistant"):
        with st.spinner("Yanıt oluşturuluyor..."):
            response, err = api_chat(user_prompt, st.session_state["token"])
            if err:
                st.error(f"{err}")
                add_message("assistant", f"Hata: {err}")
            else:
                st.markdown(response or "")
                add_message("assistant", response or "")
    
    # Sayfayı yenile - örnek soruların kaybolması için
    # use_container_width=False ile URL değişikliğini minimize et
    st.rerun()

# Footer
st.divider()
st.caption(f"© {COMPANY_NAME} AI Chat Demo - Kurumsal İletişim Asistanı")
