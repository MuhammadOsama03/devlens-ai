from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status

from .config import settings
from .runtime import RuntimeServices, build_runtime


@lru_cache(maxsize=1)
def get_runtime() -> RuntimeServices:
    """Build shared process services once and reuse them across requests."""
    return build_runtime(settings)


def reset_runtime() -> None:
    """Discard process services after configuration changes or in tests."""
    get_runtime.cache_clear()


def enforce_rate_limit(
    request: Request,
    runtime: RuntimeServices = Depends(get_runtime),
) -> None:
    identity = request.client.host if request.client else "unknown"
    if not runtime.rate_limiter.allow(identity):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Request limit exceeded",
            headers={"Retry-After": str(int(runtime.rate_limiter.window_seconds))},
        )
