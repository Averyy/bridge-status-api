import pytest
from datetime import datetime, timedelta
from bridge_status import format_display_data

@pytest.fixture
def base_time_and_stat():
    current_time = datetime(2024, 6, 24, 18, 0, 0)  # 6:00 PM
    base_stat = {
        "last_status_change": (current_time - timedelta(minutes=35)).isoformat(),
        "avg_raising_soon_to_unavailable": 15,
        "avg_closure_duration": 30,
        "closures": [{"start": (current_time - timedelta(minutes=49)).isoformat()}]
    }
    return current_time, base_stat

def test_available(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Available", None, current_time, base_stat)
    assert status == "OPEN NOW"
    assert info == "Opened 5:25pm"
    assert icon == "checkmark.circle"

def test_available_raising_soon(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Available", "Raising Soon", current_time, base_stat)
    assert status == "OPEN NOW"
    assert info == "Closing in 1m"
    assert icon == "checkmark.circle.trianglebadge.exclamationmark"

def test_unavailable(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    base_stat["closures"][-1]["end"] = current_time.isoformat()
    status, info, icon = format_display_data("Unavailable", None, current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info == "Closed 5:11pm, opening soon"
    assert icon == "exclamationmark.triangle"

def test_unavailable_fully_raised(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Fully Raised since 17:15", current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info == "Closed 5:11pm, fully raised since 5:15pm"
    assert icon == "exclamationmark.triangle"

def test_unavailable_lowering(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Lowering", current_time, base_stat)
    assert status == "OPENING..."
    assert info == "Opening right now..."
    assert icon == "clock.arrow.trianglehead.counterclockwise.rotate.90"

def test_unavailable_raising(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Raising", current_time, base_stat)
    assert status == "CLOSING..."
    assert info == "Closed 5:25pm"
    assert icon == "exclamationmark.triangle"

def test_temporarily_unavailable(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Temporarily Unavailable", None, current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info == "Temporarily Unavailable"
    assert icon == "exclamationmark.triangle"

def test_closed_construction(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Closed Construction", None, current_time, base_stat)
    assert status == "UNKNOWN"
    assert info == "Closed Construction"
    assert icon == "questionmark.diamond"

def test_time_precision(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    base_stat["last_status_change"] = (current_time - timedelta(hours=1, minutes=7)).isoformat()
    status, info, icon = format_display_data("Available", None, current_time, base_stat)
    assert status == "OPEN NOW"
    assert info == "Opened 4:53pm"
    assert icon == "checkmark.circle"

def test_overnight_closure(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    overnight_time = current_time.replace(hour=1, minute=30)  # 1:30 AM next day
    base_stat["closures"] = [{"start": (overnight_time - timedelta(hours=3)).isoformat(), "end": overnight_time.isoformat()}]
    base_stat["avg_closure_duration"] = 240  # 4 hours
    base_stat["last_status_change"] = (overnight_time - timedelta(hours=3)).isoformat()
    status, info, icon = format_display_data("Unavailable", None, overnight_time, base_stat)
    assert status == "CLOSED NOW"
    assert info.startswith("Closed 10:30pm")
    assert "opens 2:30am in 60m" in info
    assert icon == "exclamationmark.triangle"

def test_unavailable_unknown_action(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("Unavailable", "Unknown Action", current_time, base_stat)
    assert status == "CLOSED NOW"
    assert info.startswith("Closed 5:11pm")
    assert "opening soon" in info  # Check for the standard unavailable message
    assert "Unknown Action" not in info  # The action status should not be appended for known statuses
    assert icon == "exclamationmark.triangle"

def test_unknown_status_with_action(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("UnknownStatus", "SomeAction", current_time, base_stat)
    assert status == "UNKNOWN"
    assert info == "UnknownStatus (SomeAction)"
    assert icon == "questionmark.diamond"

def test_unknown_status_without_action(base_time_and_stat):
    current_time, base_stat = base_time_and_stat
    status, info, icon = format_display_data("UnknownStatus", None, current_time, base_stat)
    assert status == "UNKNOWN"
    assert info == "UnknownStatus"
    assert icon == "questionmark.diamond"