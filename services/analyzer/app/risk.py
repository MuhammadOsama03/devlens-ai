from typing import Any


def assess_delivery_risk(overview: dict[str, Any]) -> dict[str, Any]:
    health = overview.get("engineering_health") or {}
    structure = overview.get("structure") or {}
    score = int(health.get("score", 0))
    signals = set(structure.get("quality_signals") or [])
    findings = []

    if "tests" not in signals:
        findings.append("No automated test signal detected.")
    if "github_automation" not in signals:
        findings.append("No GitHub automation signal detected.")
    if "documentation" not in signals:
        findings.append("No documentation signal detected.")

    risk_points = (100 - max(0, min(score, 100))) + len(findings) * 5
    if risk_points >= 70:
        level = "high"
    elif risk_points >= 35:
        level = "medium"
    else:
        level = "low"
    return {"level": level, "risk_points": min(risk_points, 100), "findings": findings}
