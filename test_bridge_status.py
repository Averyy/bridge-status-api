import pytest
import requests
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bridge_status import fetch_bridge_status, get_current_bridge_status, bridge_data, get_current_time
from config import local_tz

def create_mock_html(status):
    return f'''
    <table id="grey_box">
        <span class="lgtextblack">London Tower</span>
        <span id="status">{status}</span>
    </table>
    '''

@pytest.fixture
def mock_datetime():
    return datetime(2024, 6, 22, 17, 5, tzinfo=local_tz)

@pytest.fixture
def mock_requests_get(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("requests.get", mock)
    return mock

def test_basic_status(mock_requests_get, mock_datetime):
    test_cases = [
        ("Available", "Available", None),
        ("Available (Raising Soon)", "Available", "Raising Soon"),
        ("Unavailable", "Unavailable", None),
        ("Unavailable (Fully Raised since 17:11)", "Unavailable", "Fully Raised"),
        ("Unavailable (Lowering soon)", "Unavailable", "Lowering soon"),
        ("Unavailable (Lowering)", "Unavailable", "Lowering"),
        ("Unavailable (Raising)", "Unavailable", "Raising"),
    ]

    for status, expected_current, expected_action in test_cases:
        with patch('bridge_status.get_current_time', return_value=mock_datetime):
            mock_requests_get.return_value.text = create_mock_html(status)
            fetch_bridge_status()
            result = get_current_bridge_status()
            assert result['bridges'][0]['status'] == expected_current
            assert result['bridges'][0]['action'] == expected_action

def test_custom_status(mock_requests_get, mock_datetime):
    test_cases = [
        ("Tester", "Tester", None),
        ("Tester (Test)", "Tester", "Test"),
        ("Tester (Action since 12:12)", "Tester", "Action"),
    ]

    for status, expected_current, expected_action in test_cases:
        with patch('bridge_status.get_current_time', return_value=mock_datetime):
            mock_requests_get.return_value.text = create_mock_html(status)
            fetch_bridge_status()
            result = get_current_bridge_status()
            assert result['bridges'][0]['status'] == expected_current
            assert result['bridges'][0]['action'] == expected_action
            if "since 12:12" in status:
                assert result['bridges'][0]['updated'].startswith('2024-06-22T12:12:00')

def test_new_bridge(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = create_mock_html("Available")
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'][0]['updated'].startswith('2024-06-22T17:05:00')

def test_status_change(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = create_mock_html("Available")
        fetch_bridge_status()

    new_time = mock_datetime + timedelta(minutes=10)
    with patch('bridge_status.get_current_time', return_value=new_time):
        mock_requests_get.return_value.text = create_mock_html("Unavailable")
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'][0]['updated'].startswith('2024-06-22T17:15:00')

def test_no_status_change(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = create_mock_html("Unavailable (Fully Raised since 17:11)")
        fetch_bridge_status()
        initial_result = get_current_bridge_status()

    new_time = mock_datetime + timedelta(minutes=10)
    with patch('bridge_status.get_current_time', return_value=new_time):
        mock_requests_get.return_value.text = create_mock_html("Unavailable (Fully Raised since 17:11)")
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'][0]['updated'] == initial_result['bridges'][0]['updated']

    action_change_time = new_time + timedelta(minutes=10)
    with patch('bridge_status.get_current_time', return_value=action_change_time):
        mock_requests_get.return_value.text = create_mock_html("Unavailable (Lowering)")
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'][0]['updated'].startswith('2024-06-22T17:25:00')

def test_multiple_updates(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = create_mock_html("Unavailable (Fully Raised since 17:11)")
        fetch_bridge_status()

    new_time = mock_datetime + timedelta(minutes=50)
    with patch('bridge_status.get_current_time', return_value=new_time):
        mock_requests_get.return_value.text = create_mock_html("Unavailable (Fully Raised since 18:00)")
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'][0]['updated'].startswith('2024-06-22T18:00:00')

def test_empty_html_response(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = ''
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'] == []

def test_malformed_html(mock_requests_get, mock_datetime):
    malformed_html = '''
    <html>
        <body>
            <div>Some random text not related to bridge status</div>
        </body>
    </html>
    '''
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = malformed_html
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'] == []

def test_network_error(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.side_effect = requests.exceptions.RequestException
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'] == []

def test_status_without_time(mock_requests_get, mock_datetime):
    status = "Unavailable"
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = create_mock_html(status)
        fetch_bridge_status()
        result = get_current_bridge_status()
        assert result['bridges'][0]['status'] == "Unavailable"
        assert result['bridges'][0]['action'] is None
        assert result['bridges'][0]['updated'].startswith('2024-06-22T17:05:00')

def test_simultaneous_updates(mock_requests_get, mock_datetime):
    with patch('bridge_status.get_current_time', return_value=mock_datetime):
        mock_requests_get.return_value.text = create_mock_html("Available")
        fetch_bridge_status()

    new_time = mock_datetime + timedelta(seconds=1)
    with patch('bridge_status.get_current_time', return_value=new_time):
        mock_requests_get.return_value.text = create_mock_html("Unavailable")
        fetch_bridge_status()

    another_time = new_time + timedelta(seconds=1)
    with patch('bridge_status.get_current_time', return_value=another_time):
        mock_requests_get.return_value.text = create_mock_html("Available")
        fetch_bridge_status()

    result = get_current_bridge_status()
    assert result['bridges'][0]['status'] == "Available"
    assert result['bridges'][0]['updated'].startswith(another_time.isoformat())