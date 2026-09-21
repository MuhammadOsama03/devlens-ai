import pytest

from app.pagination import paginate


def test_paginate_returns_metadata_and_has_more():
    page = paginate(["a", "b", "c"], offset=1, limit=1)
    assert page.items == ["b"]
    assert page.total == 3
    assert page.has_more


@pytest.mark.parametrize(("offset", "limit"), [(-1, 10), (0, 0), (0, 101)])
def test_paginate_rejects_invalid_bounds(offset, limit):
    with pytest.raises(ValueError):
        paginate([], offset=offset, limit=limit)
