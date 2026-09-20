from app.reports import build_markdown_report


def test_build_markdown_report_summarizes_overview():
    report = build_markdown_report(
        {
            "repository": "example/project",
            "summary": {"languages": {"Python": 75.0, "HTML": 25.0}},
            "engineering_health": {"score": 80, "grade": "A", "recommendations": ["Add license."]},
            "structure": {"file_count": 4, "directory_count": 2},
        }
    )
    assert "# DevLens Report: example/project" in report
    assert "Python 75.0%" in report
    assert "80/100 (A)" in report
    assert "- Add license." in report
