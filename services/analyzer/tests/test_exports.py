import json

from app.exports import export_json, export_summary_csv


def test_export_json_is_stable_and_readable():
    exported = export_json({"b": 2, "a": 1})
    assert json.loads(exported) == {"a": 1, "b": 2}
    assert exported.index('"a"') < exported.index('"b"')


def test_export_summary_csv_flattens_key_metrics():
    exported = export_summary_csv({
        "repository": "example/project",
        "summary": {"stars": 4, "forks": 2},
        "engineering_health": {"score": 80, "grade": "A"},
    })
    assert "repository,stars,forks,health_score,health_grade" in exported
    assert "example/project,4,2,80,A" in exported
