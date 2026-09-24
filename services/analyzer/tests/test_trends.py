from app.trends import summarize_daily_commits


def test_summarize_daily_commits_groups_valid_dates():
    commits = [
        {"commit": {"author": {"date": "2026-09-24T10:00:00Z"}}},
        {"commit": {"author": {"date": "2026-09-24T11:00:00Z"}}},
        {"commit": {"author": {"date": "2026-09-23T11:00:00Z"}}},
        {"commit": {"author": {"date": "invalid"}}},
    ]
    assert summarize_daily_commits(commits) == [
        {"date": "2026-09-23", "commits": 1},
        {"date": "2026-09-24", "commits": 2},
    ]
