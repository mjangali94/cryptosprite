# tests/test_ai_tools_date.py
import pytest
from ai.tools.resolve_date_range import get_today_date, resolve_date_range
from datetime import datetime, timedelta


# ------------------------- get_today_date -------------------------
def test_get_today_date_returns_string():
    """get_today_date should return a string in YYYY-MM-DD format."""
    result = get_today_date.invoke({})
    today_str = datetime.today().strftime("%Y-%m-%d")
    assert isinstance(result, str)
    assert result == today_str


# ------------------------- resolve_date_range -------------------------
def test_resolve_today():
    """Test parsing 'today' keyword."""
    result = resolve_date_range.invoke({"date_str": "today"})
    today = datetime.today().strftime("%Y-%m-%d")
    assert result["dates"] == [today]


def test_resolve_yesterday():
    """Test parsing 'yesterday' keyword."""
    result = resolve_date_range.invoke({"date_str": "yesterday"})
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    assert result["dates"] == [yesterday]


def test_resolve_last_3_days():
    """Test parsing 'last 3 days' range."""
    result = resolve_date_range.invoke({"date_str": "last 3 days"})
    today = datetime.today().date()
    expected = [(today - timedelta(days=2) + timedelta(days=i)).isoformat() for i in range(3)]
    assert result["dates"] == expected


def test_resolve_2_days_ago():
    """Test parsing '2 days ago'."""
    result = resolve_date_range.invoke({"date_str": "2 days ago"})
    target = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    assert result["dates"] == [target]


def test_resolve_last_2_weeks():
    """Test parsing 'last 2 weeks' range."""
    result = resolve_date_range.invoke({"date_str": "last 2 weeks"})
    today = datetime.today().date()
    start_date = today - timedelta(weeks=2 - 1)
    expected = [(start_date + timedelta(days=i)).isoformat() for i in range((today - start_date).days + 1)]
    assert result["dates"] == expected


def test_resolve_1_month_ago():
    """Test parsing '1 month ago'."""
    result = resolve_date_range.invoke({"date_str": "1 month ago"})
    target = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    assert result["dates"] == [target]


def test_resolve_last_2_months():
    """Test parsing 'last 2 months' range."""
    result = resolve_date_range.invoke({"date_str": "last 2 months"})
    today = datetime.today().date()
    start_date = today - timedelta(days=30 * (2 - 1))
    expected = [(start_date + timedelta(days=i)).isoformat() for i in range((today - start_date).days + 1)]
    assert result["dates"] == expected


def test_resolve_absolute_date():
    """Test parsing absolute date string."""
    result = resolve_date_range.invoke({"date_str": "2025-01-01"})
    assert result["dates"] == ["2025-01-01"]


def test_resolve_invalid_date():
    """Test invalid string returns error."""
    result = resolve_date_range.invoke({"date_str": "not a date"})
    assert "error" in result
    assert "Could not parse date string" in result["error"]