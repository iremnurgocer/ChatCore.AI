from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router  # <== bu satır önemli!

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Giriş sistemi
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Backend aktif"}

@app.post("/api/chat")
def chat(request: dict):
    from ai_service import ask_ai
    prompt = request.get("prompt", "")
    result = ask_ai(prompt)
    return {"response": result}
