from config import config
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("Authorization")

        if api_key != config.api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        response = await call_next(request)
        return response
