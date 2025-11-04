"""
FastAPI Ana Uygulama - Kurumsal AI Chat API
Profesyonel, güvenli ve entegrasyona hazır chat uygulamaları için API
"""
import time
import os
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import jwt
from datetime import datetime

# Diğer modüller
from auth import router as auth_router, verify_token
from ai_service import ask_ai
from data_loader import load_json_data
from session_manager import session_manager
from logger import APILogger, ErrorCategory
from analytics import analytics
from nlp_service import IntentClassifier
from security import SecurityValidator, default_rate_limiter, strict_rate_limiter

# Uygulama yapılandırması
COMPANY_NAME = os.getenv("COMPANY_NAME", "Company1")
APP_NAME = os.getenv("APP_NAME", "Enterprise AI Chat API")

app = FastAPI(
    title=APP_NAME,
    description="Kurumsal uygulamalar için RAG desteğine sahip profesyonel AI destekli chat API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Yapılandırması - Production için güncellenmeli
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Auth router'ı dahil et
app.include_router(auth_router)

# İstek Loglama Middleware'i
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Tüm istekleri loglar ve yanıt süresini ölçer"""
    start_time = time.time()
    
    # Login endpoint'ine gelen istekleri logla
    if request.url.path == "/api/login":
        pass  # Login endpoint kendi loglarını yapıyor
    
    response = await call_next(request)
    
    process_time = time.time() - start_time

    # Token'dan user_id çıkar
    user_id = None
    ip_address = request.client.host if request.client else "unknown"
    
    # Login endpoint'ine gelen yanıtı logla
    if request.url.path == "/api/login":
        pass  # Login endpoint kendi loglarını yapıyor
    
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token_parts = auth_header.split(" ")
            if len(token_parts) >= 2:
                token = token_parts[1]
                payload = jwt.decode(token, os.getenv("SECRET_KEY", "supersecret"), algorithms=["HS256"])
                user_id = payload.get("sub")
                if user_id:
                    request.state.user_id = user_id
    except jwt.ExpiredSignatureError:
        APILogger.log_security_event("TOKEN_EXPIRED", f"Expired token from {ip_address}", None, ip_address)
    except jwt.InvalidTokenError:
        APILogger.log_security_event("INVALID_TOKEN", f"Invalid token from {ip_address}", None, ip_address)
    except Exception:
        # Token doğrulama başarısız, user_id olmadan devam et
        pass

    # Rate limiting kontrolü (status ve login endpoint'leri hariç)
    # Login endpoint'i kendi rate limiting'ini yapıyor (strict_rate_limiter)
    if request.url.path not in ["/api/status", "/api/login"]:
        identifier = ip_address
        if hasattr(request.state, 'user_id'):
            identifier = f"{identifier}:{request.state.user_id}"
        
        if not default_rate_limiter.is_allowed(identifier):
            APILogger.log_security_event("RATE_LIMIT", f"Rate limit exceeded for {identifier}", user_id, ip_address)
            response = JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Please try again later."}
            )
            return response

    # İsteği logla
    APILogger.log_request(
        endpoint=str(request.url.path),
        method=request.method,
        user_id=user_id,
        response_time=process_time
    )
    
    # Analytics
    analytics.record_request(str(request.url.path), process_time, response.status_code < 400)

    # Güvenlik header'ları ekle
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response

# Dependency: Token Doğrulama
def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Token'dan kullanıcıyı çıkar ve doğrula"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token_parts = authorization.split(" ")
    if len(token_parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = token_parts[1]
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "supersecret"), algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        APILogger.log_security_event("TOKEN_EXPIRED", "Token expired", None, None)
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        APILogger.log_security_event("INVALID_TOKEN", "Invalid token", None, None)
        raise HTTPException(status_code=401, detail="Invalid token")

# API Endpoints

@app.get("/")
def root():
    """Root endpoint - Servis durumu"""
    return {
        "name": APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "company": COMPANY_NAME
    }

@app.get("/api/status")
def get_status():
    """Sağlık kontrolü endpoint'i"""
    try:
        data = load_json_data()
        
        # TinyDB'den session sayısını al
        session_count = len(session_manager.sessions_table.all())
        
        # Procedures sayısını da ekle (eğer varsa)
        procedures_count = len(data.get("procedures", []))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "employees": len(data.get("employees", [])),
                "departments": len(data.get("departments", [])),
                "projects": len(data.get("projects", [])),
                "procedures": procedures_count
            },
            "ai_provider": os.getenv("AI_PROVIDER", "GEMINI"),
            "session_count": session_count,
            "version": "1.0.0"
        }
    except Exception as e:
        APILogger.log_error("/api/status", e, None, ErrorCategory.CONFIG_ERROR)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/employees")
def get_employees(user_id: str = Depends(get_current_user)):
    """Çalışan listesini getirir"""
    try:
        data = load_json_data()
        employees = data.get("employees", [])
        
        APILogger.log_request("/api/employees", "GET", user_id)
        
        return {
            "success": True,
            "count": len(employees),
            "employees": employees
        }
    except FileNotFoundError as e:
        APILogger.log_error("/api/employees", e, user_id, ErrorCategory.DATABASE_ERROR)
        analytics.record_error("/api/employees", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        APILogger.log_error("/api/employees", e, user_id, ErrorCategory.DATABASE_ERROR)
        analytics.record_error("/api/employees", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

@app.get("/api/navigator")
def get_navigator_info(request: Request, user_id: str = Depends(get_current_user)):
    """Navigator bilgilerini getirir (user agent, platform, oscpu vb.)"""
    try:
        import platform
        
        # User-Agent header'ından bilgi al
        user_agent = request.headers.get("User-Agent", "")
        
        # OS bilgisi
        os_name = platform.system()
        os_version = platform.version()
        os_arch = platform.machine()
        
        # oscpu formatı: Windows NT 10.0; Win64; x64 gibi
        if os_name == "Windows":
            if "64" in os_arch:
                oscpu = f"Windows NT {os_version.split('.')[0]}.{os_version.split('.')[1] if '.' in os_version else '0'}; Win64; x64"
            else:
                oscpu = f"Windows NT {os_version.split('.')[0]}.{os_version.split('.')[1] if '.' in os_version else '0'}; Win32"
        elif os_name == "Linux":
            oscpu = f"Linux {os_arch}"
        elif os_name == "Darwin":
            oscpu = f"Intel Mac OS X {os_version}"
        else:
            oscpu = f"{os_name} {os_version}"
        
        return {
            "success": True,
            "oscpu": oscpu,
            "platform": platform.platform(),
            "user_agent": user_agent,
            "language": request.headers.get("Accept-Language", "en-US")
        }
    except Exception as e:
        APILogger.log_error("/api/navigator", e, user_id, ErrorCategory.CONFIG_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to get navigator info: {str(e)}")

@app.get("/api/departments")
def get_departments(user_id: str = Depends(get_current_user)):
    """Departman listesini getirir"""
    try:
        data = load_json_data()
        departments = data.get("departments", [])
        
        APILogger.log_request("/api/departments", "GET", user_id)
        
        return {
            "success": True,
            "count": len(departments),
            "departments": departments
        }
    except FileNotFoundError as e:
        APILogger.log_error("/api/departments", e, user_id, ErrorCategory.DATABASE_ERROR)
        analytics.record_error("/api/departments", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        APILogger.log_error("/api/departments", e, user_id, ErrorCategory.DATABASE_ERROR)
        analytics.record_error("/api/departments", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

@app.get("/api/projects")
def get_projects(user_id: str = Depends(get_current_user)):
    """Proje listesini getirir"""
    try:
        data = load_json_data()
        projects = data.get("projects", [])
        
        APILogger.log_request("/api/projects", "GET", user_id)
        
        return {
            "success": True,
            "count": len(projects),
            "projects": projects
        }
    except FileNotFoundError as e:
        APILogger.log_error("/api/projects", e, user_id, ErrorCategory.DATABASE_ERROR)
        analytics.record_error("/api/projects", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        APILogger.log_error("/api/projects", e, user_id, ErrorCategory.DATABASE_ERROR)
        analytics.record_error("/api/projects", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

@app.post("/api/chat")
def chat(request: dict, user_id: str = Depends(get_current_user)):
    """
    Ana chat endpoint'i - AI sohbeti
    
    Her kullanıcı için izole conversation'lar yönetir.
    ChatGPT gibi her conversation ayrı bir sohbet olarak çalışır.
    """
    start_time = time.time()
    
    prompt = request.get("prompt", "")
    conversation_id = request.get("conversation_id")  # URL'den gelen conversation ID
    
    if not prompt or not prompt.strip():
        APILogger.log_error("/api/chat", ValueError("Empty prompt"), user_id, ErrorCategory.VALIDATION_ERROR)
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Input doğrulama ve temizleme
    ip_address = None
    try:
        prompt = SecurityValidator.sanitize_input(prompt, user_id, ip_address)
    except HTTPException as e:
        APILogger.log_security_event("VALIDATION_ERROR", f"Invalid input detected: {prompt[:50]}", user_id, None)
        raise
    
    try:
        # Conversation ID varsa onu kullan, yoksa aktif conversation'ı kullan
        if conversation_id:
            # Conversation'ın kullanıcıya ait olduğunu kontrol et
            conv = session_manager.get_conversation(conversation_id, user_id)
            if not conv:
                # Conversation bulunamad� veya kullan�c�ya ait de�il, yeni olu�tur
                conversation_id = session_manager.create_conversation(user_id)
                session_manager.set_active_conversation(user_id, conversation_id)
            else:
                # Conversation bulundu ve kullanıcıya ait, aktif yap
                session_manager.set_active_conversation(user_id, conversation_id)
        else:
            # Conversation ID yoksa aktif conversation'ı kullan
            conversation_id = session_manager.get_active_conversation_id(user_id)
            if not conversation_id:
                # Aktif conversation da yoksa yeni olu�tur
                conversation_id = session_manager.create_conversation(user_id)
                session_manager.set_active_conversation(user_id, conversation_id)
        
        # Conversation ge�mi�ini al
        conversation_history = session_manager.get_conversation_history(user_id, conversation_id=conversation_id)

        # AI yanıtını al (user_id ile kullanıcı bazlı cache)
        response = ask_ai(prompt, conversation_history, user_id=user_id)
        
        # Session'a kaydet (conversation_id ile)
        session_manager.add_message(user_id, "user", prompt, conversation_id=conversation_id)
        session_manager.add_message(user_id, "assistant", response, conversation_id=conversation_id)
        
        # Son aktivite zamanını güncelle
        session_manager.update_last_activity(user_id)
        
        # Log
        response_time = time.time() - start_time
        APILogger.log_chat_query(user_id, prompt, response, response_time)
        
        return {
            "success": True,
            "response": response,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        APILogger.log_error("/api/chat", e, user_id, ErrorCategory.AI_ERROR)
        analytics.record_error("/api/chat", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@app.post("/api/ask")
def ask_rag(request: dict, user_id: str = Depends(get_current_user)):
    """RAG pipeline sorgu endpoint'i"""
    start_time = time.time()
    
    query = request.get("query", "")
    if not query:
        APILogger.log_error("/api/ask", ValueError("Empty query"), user_id, ErrorCategory.VALIDATION_ERROR)
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Input do�rulama ve temizleme
    ip_address = None
    try:
        query = SecurityValidator.sanitize_input(query, user_id, ip_address)
    except HTTPException as e:
        APILogger.log_security_event("VALIDATION_ERROR", f"Invalid input detected: {query[:50]}", user_id, None)
        raise
    
    try:
        # Intent ve entity çıkarımı
        analysis = IntentClassifier.analyze_query(query)

        # AI yanıtını al (performans için: advanced_rag=False, fallback=False, user_id ile kullanıcı bazlı cache)
        conversation_history = session_manager.get_conversation_history(user_id)
        response = ask_ai(query, conversation_history, use_advanced_rag=False, use_fallback=False, user_id=user_id)
        
        # Session'a kaydet
        session_manager.add_message(user_id, "user", query)
        session_manager.add_message(user_id, "assistant", response)
        
        # Log
        response_time = time.time() - start_time
        APILogger.log_chat_query(user_id, query, response, response_time)
        
        return {
            "success": True,
            "query": query,
            "response": response,
            "analysis": analysis,
            "response_time_ms": response_time * 1000,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        APILogger.log_error("/api/ask", e, user_id, ErrorCategory.AI_ERROR)
        analytics.record_error("/api/ask", type(e).__name__, str(e))
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/api/stats")
def get_stats(user_id: str = Depends(get_current_user)):
    """Analytics ve istatistikler"""
    try:
        stats = analytics.get_stats()
        
        # Session istatistiklerini ekle (TinyDB'den)
        from datetime import datetime, timedelta
        all_sessions = session_manager.sessions_table.all()
        stats["session_count"] = len(all_sessions)
        
        now = datetime.now()
        active_count = 0
        for session in all_sessions:
            last_activity_str = session.get("last_activity", "")
            if last_activity_str:
                try:
                    if isinstance(last_activity_str, str):
                        last_activity = datetime.fromisoformat(last_activity_str)
                    else:
                        last_activity = now
                    
                    if (now - last_activity).total_seconds() < 3600:
                        active_count += 1
                except:
                    continue
        
        stats["active_users"] = active_count
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        APILogger.log_error("/api/stats", e, user_id, ErrorCategory.CONFIG_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str, user_id: str = Depends(get_current_user), conversation_id: Optional[str] = Query(None)):
    """Session bilgilerini getirir - conversation_id belirtilmişse onun mesajlarını, yoksa aktif conversation'ın mesajlarını döner"""
    if session_id != user_id:
        APILogger.log_security_event("UNAUTHORIZED_ACCESS", f"User {user_id} tried to access session {session_id}", user_id, None)
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Conversation ID belirtilmişse onun mesajlarını getir, yoksa aktif conversation'ı kullan
        if conversation_id:
            # Conversation'ın kullanıcıya ait olduğunu kontrol et
            conv = session_manager.get_conversation(conversation_id, user_id)
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")
            history = session_manager.get_conversation_history(user_id, conversation_id=conversation_id)
        else:
            # Aktif conversation'ın geçmişini getir
            history = session_manager.get_conversation_history(user_id)  # conversation_id None, aktif conversation'ı kullanır
        
        context = session_manager.get_context(user_id)
        
        return {
            "success": True,
            "session_id": user_id,
            "conversation_id": conversation_id or session_manager.get_active_conversation_id(user_id),
            "message_count": len(history),
            "messages": history,
            "context": context
        }
    except HTTPException:
        raise
    except Exception as e:
        APILogger.log_error(f"/api/sessions/{session_id}", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@app.delete("/api/sessions/{session_id}")
def clear_session(session_id: str, user_id: str = Depends(get_current_user)):
    """Session'ı temizler"""
    if session_id != user_id:
        APILogger.log_security_event("UNAUTHORIZED_ACCESS", f"User {user_id} tried to clear session {session_id}", user_id, None)
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        session_manager.clear_session(user_id)
        return {"success": True, "message": "Session cleared"}
    except Exception as e:
        APILogger.log_error(f"/api/sessions/{session_id}", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")

@app.get("/api/procedures")
def get_procedures(user_id: str = Depends(get_current_user)):
    """Tüm prosedürleri getirir"""
    try:
        procedures = load_json_data("procedures.json")
        return {
            "success": True,
            "procedures": procedures,
            "count": len(procedures) if isinstance(procedures, list) else 1
        }
    except Exception as e:
        APILogger.log_error("/api/procedures", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve procedures: {str(e)}")

@app.get("/api/procedures/new")
def get_new_procedures(
    days: int = 30,
    user_id: str = Depends(get_current_user)
):
    """Belirli bir tarihten sonra yayınlanan yeni prosedürleri getirir"""
    try:
        from datetime import datetime, timedelta
        
        procedures = load_json_data("procedures.json")
        if not isinstance(procedures, list):
            procedures = [procedures]
        
        # Tarih filtresi
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Kullanıcının görüntülediği prosedürleri al
        viewed_procedure_ids = session_manager.get_viewed_procedures(user_id)
        
        new_procedures = []
        for proc in procedures:
            try:
                published_date_str = proc.get("published_date", "")
                if published_date_str:
                    published_date = datetime.fromisoformat(published_date_str.replace("Z", "+00:00"))
                    if published_date >= cutoff_date:
                        proc_id = proc.get("id")
                        # Kullanıcının görüntülemediği prosedürleri ekle
                        if proc_id not in viewed_procedure_ids:
                            new_procedures.append({
                                **proc,
                                "is_new": True,
                                "days_since_published": (datetime.now() - published_date).days
                            })
            except Exception:
                continue
        
        # Tarihe göre sırala (en yeniler önce)
        new_procedures.sort(key=lambda x: x.get("published_date", ""), reverse=True)
        
        return {
            "success": True,
            "new_procedures": new_procedures,
            "count": len(new_procedures),
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        APILogger.log_error("/api/procedures/new", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve new procedures: {str(e)}")

@app.get("/api/conversations")
def get_conversations(user_id: str = Depends(get_current_user)):
    """
    Kullanıcının tüm conversation'larını getirir
    
    Her kullanıcı sadece kendi conversation'larını görür.
    ChatGPT gibi her conversation ayrı bir sohbet olarak gösterilir.
    """
    try:
        conversations = session_manager.get_user_conversations(user_id)
        active_conv_id = session_manager.get_active_conversation_id(user_id)
        
        # Boş conversation'ları temizle
        session_manager.cleanup_empty_conversations(user_id)
        
        # Her conversation için bilgi hazırla
        conv_list = []
        for conv in conversations:
            conv_list.append({
                "conversation_id": conv.get("conversation_id"),
                "title": conv.get("title", "Yeni Sohbet"),
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at"),
                "message_count": conv.get("message_count", 0),
                "is_active": conv.get("conversation_id") == active_conv_id
            })
        
        return {
            "success": True,
            "conversations": conv_list,
            "active_conversation_id": active_conv_id,
            "count": len(conv_list)
        }
    except Exception as e:
        APILogger.log_error("/api/conversations", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")

@app.post("/api/conversations/new")
def create_conversation(user_id: str = Depends(get_current_user)):
    """
    Yeni conversation oluşturur - ChatGPT gibi her kullanıcı için ayrı conversation'lar
    
    Her kullanıcı kendi conversation'larını görür ve yönetir.
    Conversation'lar kullanıcı bazlı izole edilmiştir.
    """
    try:
        conversation_id = session_manager.create_conversation(user_id)
        session_manager.set_active_conversation(user_id, conversation_id)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "message": "Yeni sohbet oluşturuldu"
        }
    except Exception as e:
        APILogger.log_error("/api/conversations/new", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@app.post("/api/conversations/{conversation_id}/switch")
def switch_conversation(conversation_id: str, user_id: str = Depends(get_current_user)):
    """Aktif conversation'ı değiştirir"""
    try:
        # Conversation'ın kullanıcıya ait olduğunu kontrol et
        conv = session_manager.get_conversation(conversation_id, user_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        session_manager.set_active_conversation(user_id, conversation_id)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "message": "Aktif sohbet değiştirildi"
        }
    except HTTPException:
        raise
    except Exception as e:
        APILogger.log_error(f"/api/conversations/{conversation_id}/switch", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to switch conversation: {str(e)}")

@app.get("/api/conversation/{conversation_id}/restore")
def restore_session_from_conversation(conversation_id: str):
    """
    Conversation ID'den session'ı restore eder (token gerektirmez - public endpoint)
    
    GÜVENLİK NOTU: Bu endpoint sadece aktif session varsa çalışmalı.
    Logout sonrası conversation'lar silindiği için restore çalışmamalı.
    """
    try:
        # Conversation'ın sahibini bul
        owner_id = session_manager.get_conversation_owner(conversation_id)
        if not owner_id:
            # Conversation bulunamadı (silinmiş veya hiç oluşturulmamış)
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Session var mı kontrol et - eğer session yoksa logout yapılmış demektir
        if not session_manager.session_exists(owner_id):
            raise HTTPException(status_code=401, detail="Session expired, please login")
        
        # Mevcut session'ı al (yeni oluşturma!)
        result = session_manager.sessions_table.search(session_manager.Query.user_id == owner_id)
        if not result:
            raise HTTPException(status_code=401, detail="Session expired, please login")
        
        session = result[0]
        token = session.get("token")
        
        if not token:
            raise HTTPException(status_code=401, detail="Session expired, please login")
        
        # Token'ı verify et
        try:
            from auth import verify_token as verify_token_func
            payload = verify_token_func(token)
            if payload:
                # Conversation'ın hala kullanıcıya ait olduğunu kontrol et
                conv = session_manager.get_conversation(conversation_id, owner_id)
                if not conv:
                    raise HTTPException(status_code=404, detail="Conversation not found")
                
                return {
                    "success": True,
                    "user_id": owner_id,
                    "token": token,
                    "conversation_id": conversation_id
                }
        except HTTPException:
            raise
        except:
            # Token geçersiz, login gerekli
            raise HTTPException(status_code=401, detail="Session expired, please login")
        
        raise HTTPException(status_code=401, detail="Invalid session")
    except HTTPException:
        raise
    except Exception as e:
        APILogger.log_error(f"/api/conversation/{conversation_id}/restore", e, None, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to restore session: {str(e)}")

@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, user_id: str = Depends(get_current_user)):
    """Conversation'ı siler"""
    try:
        # Conversation'ın kullanıcıya ait olduğunu kontrol et
        conv = session_manager.get_conversation(conversation_id, user_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        session_manager.delete_conversation(conversation_id, user_id)
        
        # Eğer silinen conversation aktifse, yeni bir tane oluştur
        active_conv_id = session_manager.get_active_conversation_id(user_id)
        if active_conv_id == conversation_id:
            new_conv_id = session_manager.create_conversation(user_id)
            session_manager.set_active_conversation(user_id, new_conv_id)
        
        return {
            "success": True,
            "message": "Sohbet silindi"
        }
    except HTTPException:
        raise
    except Exception as e:
        APILogger.log_error(f"/api/conversations/{conversation_id}", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@app.post("/api/procedures/{procedure_id}/mark-viewed")
def mark_procedure_viewed(
    procedure_id: int,
    user_id: str = Depends(get_current_user)
):
    """Prosedürün görüntülendiğini işaretle"""
    try:
        session_manager.mark_procedure_viewed(user_id, procedure_id)
        session_manager.update_last_activity(user_id)
        return {
            "success": True,
            "message": f"Procedure {procedure_id} marked as viewed"
        }
    except Exception as e:
        APILogger.log_error(f"/api/procedures/{procedure_id}/mark-viewed", e, user_id, ErrorCategory.DATABASE_ERROR)
        raise HTTPException(status_code=500, detail=f"Failed to mark procedure as viewed: {str(e)}")

# Hata Yönetici
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception'larını yönetir"""
    category = ErrorCategory.VALIDATION_ERROR if exc.status_code < 500 else ErrorCategory.UNKNOWN_ERROR
    APILogger.log_error(str(request.url.path), exc, None, category)
    analytics.record_error(str(request.url.path), "HTTPException", exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Genel exception'ları yönetir"""
    APILogger.log_error(str(request.url.path), exc, None, ErrorCategory.UNKNOWN_ERROR)
    analytics.record_error(str(request.url.path), type(exc).__name__, str(exc))
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
