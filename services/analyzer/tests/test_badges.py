from app.badges import build_health_badge


def test_build_health_badge_bounds_score_and_maps_grade():
    badge = build_health_badge(120, "a")
    assert badge["message"] == "100/100 A"
    assert badge["color"] == "2ea44f"
    assert "img.shields.io" in badge["url"]


def test_build_health_badge_falls_back_to_failure_grade():
    assert build_health_badge(-5, "unknown")["message"] == "0/100 F"
