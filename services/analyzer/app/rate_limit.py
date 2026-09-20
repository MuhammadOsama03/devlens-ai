from collections import defaultdict, deque
from threading import RLock
from time import monotonic


class RateLimiter:
    def __init__(self, limit: int = 60, window_seconds: float = 60):
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()

    def allow(self, identity: str, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        cutoff = current - self.window_seconds
        with self._lock:
            requests = self._requests[identity]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self.limit:
                return False
            requests.append(current)
            return True
