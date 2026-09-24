from dataclasses import dataclass

from .cache import TTLCache
from .config import Settings
from .rate_limit import RateLimiter
from .storage import AnalysisStore


@dataclass(frozen=True)
class RuntimeServices:
    cache: TTLCache[dict]
    store: AnalysisStore
    rate_limiter: RateLimiter


def build_runtime(settings: Settings) -> RuntimeServices:
    return RuntimeServices(
        cache=TTLCache(
            ttl_seconds=settings.cache_ttl_seconds,
            max_entries=settings.cache_max_entries,
        ),
        store=AnalysisStore(settings.database_path),
        rate_limiter=RateLimiter(
            limit=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        ),
    )
