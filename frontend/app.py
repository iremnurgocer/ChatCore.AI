import os
import json
import requests
import streamlit as st

# ---------- Ayarlar ----------
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="ChatCore.AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Yardımcılar ----------
def api_login(username: str, password: str):
    url = f"{BACKEND_URL}/api/login"
    try:
        r = requests.post(url, json={"username": username, "password": password}, timeout=15)
        if r.status_code == 200:
            return r.json().get("token"), None
        # Hata mesajını backend'den alabiliyorsak göster
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        return None, f"Giriş başarısız ({r.status_code}): {detail}"
    except requests.RequestException as e:
        return None, f"Sunucuya ulaşılamıyor: {e}"

def api_chat(prompt: str, token: str):
    url = f"{BACKEND_URL}/api/chat"
    try:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"} if token else {},
            json={"prompt": prompt},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json().get("response"), None
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        return None, f"API hata döndürdü ({r.status_code}): {detail}"
    except requests.RequestException as e:
        return None, f"Ağ hatası: {e}"

def ensure_state():
    for k, v in [
        ("token", None),
        ("username", None),
        ("messages", []),  # [{"role":"user"/"assistant","content": "..."}]
    ]:
        if k not in st.session_state:
            st.session_state[k] = v

def add_message(role, content):
    st.session_state["messages"].append({"role": role, "content": content})

# ---------- Arayüz ----------
ensure_state()

# Üst başlık
st.markdown(
    """
    <div style="text-align:center; margin-top:1rem; margin-bottom:0.5rem;">
      <h1 style="margin-bottom:0.2rem;">ChatCore.AI Asistanı</h1>
      <p style="opacity:0.7; margin-top:0;">Kurumsal destekli bilgi asistanı</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------- GİRİŞ EKRANI ----------
if not st.session_state["token"]:
    with st.container():
        st.subheader("Giriş Yap", divider="gray")
        col1, col2 = st.columns([1, 1])
        with col1:
            username = st.text_input("Kullanıcı adı", value=st.session_state.get("username") or "", placeholder="admin")
        with col2:
            password = st.text_input("Şifre", type="password", value="", placeholder="••••")

        login_btn = st.button("Giriş Yap", type="primary", use_container_width=True)
        if login_btn:
            token, err = api_login(username.strip(), password)
            if token:
                st.session_state["token"] = token
                st.session_state["username"] = username.strip()
                st.success("Giriş başarılı, yönlendiriliyorsunuz…")
                st.rerun()
            else:
                st.error(err or "Kullanıcı adı veya şifre hatalı.")

    st.caption(f"Backend: `{BACKEND_URL}`")
    st.stop()

# --------- SOHBET EKRANI ----------
# Sidebar: kullanıcı / çıkış
with st.sidebar:
    st.markdown("### Ayarlar")
    st.write(f"👤 **{st.session_state['username']}**")
    if st.button("Çıkış Yap"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.divider()
    st.caption(f"Backend: `{BACKEND_URL}`")

# Mesaj geçmişi
for m in st.session_state["messages"]:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

# Girdi
user_prompt = st.chat_input("Mesajınızı yazın…")
if user_prompt:
    # Kullanıcı mesajını ekrana bas
    add_message("user", user_prompt)
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Backend'e gönder
    with st.chat_message("assistant"):
        with st.spinner("Yanıt oluşturuluyor…"):
            response, err = api_chat(user_prompt, st.session_state["token"])
            if err:
                st.warning(f"{err}")
                add_message("assistant", f"{err}")
            else:
                st.markdown(response or "")
                add_message("assistant", response or "")

# Alt alan: PDF export vb. (istersen sonra eklersin)
st.divider()
st.caption("© ChatCore.AI • Demo")
