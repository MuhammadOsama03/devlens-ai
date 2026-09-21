from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    offset: int
    limit: int
    total: int

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total


def paginate(items: Sequence[T], offset: int = 0, limit: int = 50) -> Page[T]:
    if offset < 0:
        raise ValueError("offset cannot be negative")
    if limit <= 0 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    return Page(list(items[offset : offset + limit]), offset, limit, len(items))
