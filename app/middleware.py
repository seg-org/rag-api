from config import config
from fastapi import HTTPException, Request


def verify_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    api_key = auth_header.replace("Bearer ", "")

    if api_key != config.app.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
