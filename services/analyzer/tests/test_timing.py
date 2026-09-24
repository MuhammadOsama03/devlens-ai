from app.timing import measure


def test_measure_records_elapsed_milliseconds():
    ticks = iter([10.0, 10.125])
    with measure("github.fetch", clock=lambda: next(ticks)) as timing:
        assert timing.operation == "github.fetch"
    assert timing.duration_ms == 125.0
