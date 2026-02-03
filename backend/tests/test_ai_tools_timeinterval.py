# tests/test_ai_tools_interval.py
import pytest
from ai.tools.time_intervals_parse import resolve_human_interval

# ------------------------- Valid Inputs -------------------------

@pytest.mark.parametrize(
    "input_str,expected_amount,expected_unit",
    [
        ("2 hours", 2, "hours"),
        ("1 hour", 1, "hours"),
        ("3 days", 3, "days"),
        ("1 day", 1, "days"),
        ("2 weeks", 14, "days"),      # 2*7
        ("1 week", 7, "days"),
        ("3 months", 90, "days"),     # 3*30
        ("1 month", 30, "days"),
        ("2.5 hours", 2.5, "hours"),  # decimal hours
        ("0.5 days", 0.5, "days"),    # decimal days
    ]
)
def test_resolve_human_interval_valid(input_str, expected_amount, expected_unit):
    result = resolve_human_interval.invoke({"interval_str": input_str})
    assert isinstance(result, dict)
    assert "original" in result
    assert result["original"] == input_str.lower().strip()
    assert result["amount"] == expected_amount
    assert result["normalized_interval"] == expected_unit

# ------------------------- Invalid Inputs -------------------------

@pytest.mark.parametrize(
    "input_str",
    [
        "five hours",       # non-numeric
        "2 lightyears",     # unsupported unit
        "2.5",              # missing unit
        "-2 hours",         # negative number
        "0 hours",          # zero amount
        "2 hourss",         # typo in unit
    ]
)
def test_resolve_human_interval_invalid(input_str):
    """Inputs that should produce an error."""
    result = resolve_human_interval.invoke({"interval_str": input_str})
    assert isinstance(result, dict)
    assert "error" in result
    assert isinstance(result["error"], str)

# ------------------------- Extra checks -------------------------

def test_resolve_human_interval_strip_whitespace():
    """Ensure leading/trailing whitespace is handled."""
    result = resolve_human_interval.invoke({"interval_str": "  3 days  "})
    assert result["amount"] == 3
    assert result["normalized_interval"] == "days"

def test_resolve_human_interval_case_insensitive():
    """Ensure uppercase/lowercase variations work."""
    result = resolve_human_interval.invoke({"interval_str": "2 HOURS"})
    assert result["amount"] == 2
    assert result["normalized_interval"] == "hours"