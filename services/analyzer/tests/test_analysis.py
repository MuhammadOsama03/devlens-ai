from app.analysis import (\n    analyze_paths,\n    analyze_root,\n    calculate_health,\n    summarize_commit_activity,\n)


def test_analyze_root_detects_framework_and_quality_signals():
    entries = [
        {"name": "README.md", "type": "file"},
        {"name": "next.config.ts", "type": "file"},
        {"name": "Dockerfile", "type": "file"},
        {"name": ".github", "type": "dir"},
        {"name": "tests", "type": "dir"},
        {"name": "src", "type": "dir"},
    ]

    result = analyze_root(entries)

    assert result["file_count"] == 3
    assert result["directory_count"] == 3
    assert "Next.js" in result["framework_signals"]
    assert "Docker" in result["framework_signals"]
    assert "documentation" in result["quality_signals"]
    assert "github_automation" in result["quality_signals"]
    assert "tests" in result["quality_signals"]
    assert "containerization" in result["quality_signals"]


def test_analyze_root_handles_empty_repository():
    assert analyze_root([]) == {
        "file_count": 0,
        "directory_count": 0,
        "files": [],
        "directories": [],
        "framework_signals": [],
        "quality_signals": [],
    }


def test_analyze_paths_detects_nested_signals_and_depth():
    result = analyze_paths(
        [
            "README.md",
            ".github/workflows/ci.yml",
            "services/api/requirements.txt",
            "services/api/tests/test_health.py",
        ]
    )

    assert result["file_count"] == 4
    assert result["directory_count"] == 5
    assert result["max_depth"] == 4
    assert result["framework_signals"] == ["Python project"]
    assert result["quality_signals"] == [
        "documentation",
        "github_automation",
        "tests",
    ]


def test_analyze_paths_handles_empty_input():
    assert analyze_paths([]) == {
        "file_count": 0,
        "directory_count": 0,
        "max_depth": 0,
        "framework_signals": [],
        "quality_signals": [],
    }


def test_calculate_health_scores_detected_signals():
    result = calculate_health(["documentation", "tests", "github_automation"])

    assert result["score"] == 70
    assert result["grade"] == "B"
    assert len(result["recommendations"]) == 2


def test_calculate_health_returns_full_score_without_recommendations():
    result = calculate_health(
        ["documentation", "license", "github_automation", "tests", "containerization"]
    )

    assert result == {"score": 100, "grade": "A", "recommendations": []}


def test_calculate_health_ignores_unknown_signals():
    result = calculate_health(["unknown"])

    assert result["score"] == 0
    assert result["grade"] == "F"


def test_summarize_commit_activity_counts_authors_and_merges():
    commits = [
        {
            "author": {"login": "alice"},
            "commit": {"author": {"date": "2026-09-13T10:00:00Z"}},
            "parents": [{"sha": "one"}],
        },
        {
            "author": {"login": "bob"},
            "commit": {"author": {"date": "2026-09-12T09:00:00Z"}},
            "parents": [{"sha": "one"}, {"sha": "two"}],
        },
        {
            "author": {"login": "alice"},
            "commit": {"author": {"date": "2026-09-11T08:00:00Z"}},
            "parents": [{"sha": "one"}],
        },
    ]

    result = summarize_commit_activity(commits)

    assert result == {
        "commit_count": 3,
        "unique_author_count": 2,
        "merge_commit_count": 1,
        "newest_commit_at": "2026-09-13T10:00:00Z",
        "oldest_commit_at": "2026-09-11T08:00:00Z",
    }


def test_summarize_commit_activity_handles_empty_history():
    assert summarize_commit_activity([]) == {
        "commit_count": 0,
        "unique_author_count": 0,
        "merge_commit_count": 0,
        "newest_commit_at": None,
        "oldest_commit_at": None,
    }
