import pytest

from app.contributors import summarize_contributors


def test_summarize_contributors_orders_by_commits_then_name():
    commits = [
        {"author": {"login": "bob"}, "commit": {}},
        {"author": {"login": "alice"}, "commit": {}},
        {"author": {"login": "bob"}, "commit": {}},
        {"author": None, "commit": {"author": {"name": "Carol"}}},
    ]
    assert summarize_contributors(commits) == [
        {"author": "bob", "commits": 2},
        {"author": "alice", "commits": 1},
        {"author": "Carol", "commits": 1},
    ]


def test_summarize_contributors_rejects_invalid_limit():
    with pytest.raises(ValueError):
        summarize_contributors([], limit=0)
