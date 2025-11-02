from fastapi import APIRouter, HTTPException
import jwt, datetime, os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

@router.post("/api/login")
def login(user: dict):
    username = user.get("username")
    password = user.get("password")

    if username == "admin" and password == "1234":
        payload = {"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"token": token}
    else:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre.")
