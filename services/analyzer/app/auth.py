from fastapi import Header, HTTPException, status

from .config import settings
from .security import extract_bearer_token, verify_api_key


def require_api_key(authorization: str | None = Header(default=None)) -> str:
    token = extract_bearer_token(authorization)
    if not settings.api_key_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured",
        )
    if token is None or not verify_api_key(token, settings.api_key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
