import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("API_KEY", "dev-secret-api-key")
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    if x_api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True
