from app.analysis import analyze_root


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
