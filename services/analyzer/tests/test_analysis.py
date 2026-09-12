from app.analysis import analyze_paths, analyze_root, calculate_health


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
