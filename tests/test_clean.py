import pandas as pd

from src.clean import add_grid, clean_records

CFG = {
    "year_min": 2000,
    "year_max": 2025,
    "max_uncertainty_m": 1000,
    "grid_deg": 0.02,
    "bbox": {"west": 57.2, "east": 57.9, "south": -20.6, "north": -19.9},
}


def rec(**kw):
    base = {
        "gbifID": "1",
        "speciesKey": 1,
        "decimalLatitude": -20.3,
        "decimalLongitude": 57.5,
        "coordinateUncertaintyInMeters": 50.0,
        "year": 2015,
        "eventDate": "2015-05-01",
        "datasetKey": "d",
        "basisOfRecord": "HUMAN_OBSERVATION",
        "occurrenceStatus": "PRESENT",
    }
    base.update(kw)
    return base


def run(rows):
    out, log = clean_records(pd.DataFrame(rows), CFG)
    return list(out["gbifID"]), log


def test_keeps_present_and_detected_status():
    ids, _ = run(
        [
            rec(),
            rec(gbifID="2", occurrenceStatus="DETECTED", eventDate="2016-01-01"),
            rec(gbifID="3", occurrenceStatus=None, eventDate="2017-01-01"),
        ]
    )
    assert ids == ["1", "2", "3"]


def test_removes_absent_fossil_and_captive():
    ids, _ = run(
        [
            rec(),
            rec(gbifID="2", occurrenceStatus="ABSENT"),
            rec(gbifID="3", occurrenceStatus="NOT_DETECTED"),
            rec(gbifID="4", basisOfRecord="FOSSIL_SPECIMEN"),
            rec(gbifID="5", basisOfRecord="LIVING_SPECIMEN"),
        ]
    )
    assert ids == ["1"]


def test_removes_outside_box_year_and_imprecise():
    ids, _ = run(
        [
            rec(),
            rec(gbifID="2", decimalLongitude=55.4),
            rec(gbifID="3", year=1990),
            rec(gbifID="4", coordinateUncertaintyInMeters=5000.0),
            rec(
                gbifID="5",
                coordinateUncertaintyInMeters=None,
                eventDate="2016-01-01",
            ),
        ]
    )
    assert ids == ["1", "5"]


def test_removes_exact_duplicates_only():
    ids, log = run(
        [rec(), rec(gbifID="2"), rec(gbifID="3", eventDate="2016-01-01")]
    )
    assert ids == ["1", "3"]
    assert log["remaining"].iloc[-1] == 2


def test_grid_cells():
    df = pd.DataFrame({"lon": [57.2, 57.221], "lat": [-20.6, -20.6]})
    out = add_grid(df, CFG)
    assert out["cell_x"].tolist() == [0, 1]
    assert out["cell_y"].tolist() == [0, 0]