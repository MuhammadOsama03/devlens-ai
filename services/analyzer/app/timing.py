from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Iterator


@dataclass
class Timing:
    operation: str
    duration_ms: float = 0.0


@contextmanager
def measure(
    operation: str,
    *,
    clock: Callable[[], float] = perf_counter,
) -> Iterator[Timing]:
    timing = Timing(operation)
    started = clock()
    try:
        yield timing
    finally:
        timing.duration_ms = round((clock() - started) * 1000, 3)
