import datetime
from models import Series
from project import (
    get_colored_status,
    render_ascii_table,
    render_last_aired,
    render_next_aired,
    stats,
)
import re
import pytest

from web import reverse_date


def test_fetch_series():
    pass


def test_fetch_aired_data():
    pass


def test_stats_no_series():
    result = stats([])
    assert re.match(
        r"Total results: .+0.+ Continuing: .+0.+ Upcoming: .+0.+ Ended: .+0.+", result
    )


def test_stats_with_series():
    result = stats(
        [
            Series(id="1", name="Series 1", status="Continuing", tvdb_id="1", thumbnail=""),
            Series(id="2", name="Series 2", status="Ended", tvdb_id="2", thumbnail=""),
            Series(id="3", name="Series 3", status="Upcoming", tvdb_id="3", thumbnail=""),
        ]
    )
    assert re.match(
        r"Total results: .+3.+ Continuing: .+1.+ Upcoming: .+1.+ Ended: .+1.+", result
    )


@pytest.mark.parametrize(
    "status,expected",
    [
        ("Continuing", r"\x1b\[30m\x1b\[42mContinuing\x1b\[0m"),
        ("Ended", r"\x1b\[30m\x1b\[41mEnded\x1b\[0m"),
        ("Upcoming", r"\x1b\[30m\x1b\[44mUpcoming\x1b\[0m"),
        ("Unknown", r"\x1b\[30mUnknown\x1b\[0m"),
    ],
)
def test_get_colored_status(status, expected):
    result = get_colored_status(
        Series(id="1", name="Series 1", status=status, tvdb_id="1", thumbnail="")
    )
    assert re.match(expected, result)


def test_render_ascii_table():
    result = render_ascii_table(
        [
            Series(id="1", name="Series 1", status="Continuing", tvdb_id="1", thumbnail=""),
            Series(id="2", name="Series 2", status="Ended", tvdb_id="2", thumbnail=""),
            Series(id="3", name="Series 3", status="Upcoming", tvdb_id="3", thumbnail=""),
        ],
        {
            "1": {"next_aired": "2021-01-01", "last_aired": "2020-01-01"},
            "2": {"next_aired": "2021-01-01", "last_aired": "2020-01-01"},
            "3": {"next_aired": "2021-01-01", "last_aired": "2020-01-01"},
        },
    )
    headers = ["Title", "Status", "Next Episode", "Last Episode"]
    for header in headers:
        assert header in result
    assert "Series 1" in result
    assert "Series 2" in result
    assert "Series 3" in result
    assert "Continuing" in result
    assert "Ended" in result
    assert "Upcoming" in result
    assert "01-01-2021" in result
    assert "01-01-2021" in result


def test_render_with_next_aired():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    result = render_next_aired(
        Series(id="1", name="Series 1", status="Continuing", tvdb_id="1", thumbnail=""),
        {"1": {"next_aired": tomorrow.strftime("%Y-%m-%d")}},
    )
    assert result == f"watch in 1 days ({tomorrow.strftime('%d-%m-%Y')})"


def test_render_no_next_aired():
    result = render_next_aired(
        Series(id="1", name="Series 1", status="Continuing", tvdb_id="1", thumbnail=""),
        {
            "1": {
                "next_aired": None,
            }
        },
    )
    assert result == "No upcoming episodes yet"


def test_render_last_aired():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    result = render_last_aired(
        Series(id="1", name="Series 1", status="Continuing", tvdb_id="1", thumbnail=""),
        {"1": {"last_aired": tomorrow.strftime("%Y-%m-%d")}},
    )
    assert result == f"{reverse_date(tomorrow.strftime('%Y-%m-%d'))}"
