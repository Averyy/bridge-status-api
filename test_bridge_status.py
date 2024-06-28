import pytest
from datetime import datetime, timedelta
from bridge_status import format_display_data

@pytest.fixture
def base_time_and_stat():
    current_time = datetime(2024, 6, 24, 18, 0, 0)  # 6:00 PM
    base_stat = {
        "last_status_change": (current_time - timedelta(minutes=35)).isoformat(),
        "avg_raising_soon_to_unavailable": 15,
        "raising_soon_ci": (10, 20),
        "avg_closure_duration": 30,
        "closure_duration_ci": (25, 35),
        "closures": [{"start": (current_time - timedelta(minutes=49)).isoformat()}]
    }
    return current_time, base_stat

def test_available(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Available", None, current_time, base_stat)
    assert status == "OPEN NOW"
    assert info == "Opened 5:25pm"
    assert icon == "checkmark"

def test_available_raising_soon_negative_time(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    base_stat['last_status_change'] = (current_time - timedelta(minutes=20)).isoformat()
    status, info, icon = format_display_data("Available", "Raising Soon", current_time, base_stat)
    assert status == "OPEN NOW"
    assert info == "Closing soon (longer than usual)"
    assert icon == "checkmarkWarning"

def test_available_raising_soon_positive_time(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    base_stat['last_status_change'] = (current_time - timedelta(minutes=5)).isoformat()
    status, info, icon = format_display_data("Available", "Raising Soon", current_time, base_stat)
    assert status == "OPEN NOW"
    assert info == "Closing in 5-15m (avg)"
    assert icon == "checkmarkWarning"

def test_unavailable_within_range(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    base_stat['closures'][-1]['start'] = (current_time - timedelta(minutes=10)).isoformat()
    status, info, icon = format_display_data("Unavailable", None, current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info == "Closed 5:50pm. Opening in 15-25m (avg)"
    assert icon == "warning"

def test_unavailable_longer_than_usual(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    base_stat['closures'][-1]['start'] = (current_time - timedelta(minutes=60)).isoformat()
    status, info, icon = format_display_data("Unavailable", None, current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info == "Closed 5:00pm for longer than usual"
    assert icon == "warning"

def test_unavailable_fully_raised(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Fully Raised since 17:15", current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info == "Closed 5:11pm, fully raised since 5:15pm"
    assert icon == "warning"

def test_unavailable_lowering(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Lowering", current_time, base_stat)
    assert status == "OPENING..."
    assert info == "Opening right now..."
    assert icon == "clock"

def test_unavailable_raising(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Raising", current_time, base_stat)
    assert status == "CLOSING..."
    assert info == "Closed 5:25pm"
    assert icon == "warning"

def test_unknown_status(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("UnknownStatus", None, current_time, base_stat)
    assert status == "UNKNOWN"
    assert info == "UnknownStatus"
    assert icon == "question"

def test_unknown_status_with_action(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("UnknownStatus", "SomeAction", current_time, base_stat)
    assert status == "UNKNOWN"
    assert info == "UnknownStatus (SomeAction)"
    assert icon == "question"