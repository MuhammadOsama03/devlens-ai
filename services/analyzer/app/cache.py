from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class _Entry(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    """Small thread-safe TTL cache for reusable repository analyses."""

    def __init__(self, ttl_seconds: float = 300, max_entries: int = 256):
        if ttl_seconds <= 0 or max_entries <= 0:
            raise ValueError("ttl_seconds and max_entries must be positive")
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: dict[str, _Entry[T]] = {}
        self._lock = RLock()

    def get(self, key: str) -> T | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= monotonic():
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: T) -> None:
        with self._lock:
            self._remove_expired()
            if key not in self._entries and len(self._entries) >= self.max_entries:
                oldest = min(self._entries, key=lambda item: self._entries[item].expires_at)
                self._entries.pop(oldest)
            self._entries[key] = _Entry(value, monotonic() + self.ttl_seconds)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def stats(self) -> dict[str, int]:
        with self._lock:
            self._remove_expired()
            return {"entries": len(self._entries), "capacity": self.max_entries}

    def _remove_expired(self) -> None:
        now = monotonic()
        expired = [key for key, entry in self._entries.items() if entry.expires_at <= now]
        for key in expired:
            self._entries.pop(key, None)
