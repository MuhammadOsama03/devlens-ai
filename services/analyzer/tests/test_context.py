import pytest

from app.context import select_context_paths


def test_select_context_paths_filters_generated_and_binary_files():
    paths = select_context_paths([
        "README.md", "src/app.py", "node_modules/pkg/index.js", "image.png",
        "dist/bundle.js", "src/app.py", "package.json",
    ])
    assert paths == ["README.md", "package.json", "src/app.py"]


def test_select_context_paths_enforces_limit():
    assert len(select_context_paths(["a.py", "b.py"], limit=1)) == 1


def test_select_context_paths_rejects_invalid_limit():
    with pytest.raises(ValueError):
        select_context_paths([], limit=0)
