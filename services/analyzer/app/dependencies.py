from functools import lru_cache

from .config import settings
from .runtime import RuntimeServices, build_runtime


@lru_cache(maxsize=1)
def get_runtime() -> RuntimeServices:
    """Build shared process services once and reuse them across requests."""
    return build_runtime(settings)


def reset_runtime() -> None:
    """Discard process services after configuration changes or in tests."""
    get_runtime.cache_clear()
