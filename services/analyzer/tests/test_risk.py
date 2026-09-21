from app.risk import assess_delivery_risk


def test_assess_delivery_risk_flags_missing_controls():
    result = assess_delivery_risk({
        "engineering_health": {"score": 40},
        "structure": {"quality_signals": ["documentation"]},
    })
    assert result["level"] == "high"
    assert len(result["findings"]) == 2


def test_assess_delivery_risk_recognizes_healthy_repository():
    result = assess_delivery_risk({
        "engineering_health": {"score": 100},
        "structure": {"quality_signals": ["documentation", "tests", "github_automation"]},
    })
    assert result == {"level": "low", "risk_points": 0, "findings": []}
