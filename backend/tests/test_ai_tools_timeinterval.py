import pytest
from ai.tools.time_intervals_parse import resolve_human_interval

@pytest.mark.parametrize(
    "input_str, expected_amount, expected_unit",
    [
        ("1 hour", 1, "hours"),
        ("2 hours", 2, "hours"),
        ("2.5 hours", 2.5, "hours"),
        ("1 day", 1, "days"),
        ("3 days", 3, "days"),
        ("1 week", 7, "days"),
        ("2 weeks", 14, "days"),
        ("1 month", 30, "days"),
        ("3 months", 90, "days"),
        ("0.5 days", 0.5, "days"),
    ]
)
def test_resolve_human_interval_success(input_str, expected_amount, expected_unit):
    """Test valid intervals."""
    try:
        result = resolve_human_interval.invoke({"interval_str": input_str})
        assert isinstance(result, dict)
        assert "error" not in result
        assert result["amount"] == expected_amount
        assert result["normalized_interval"] == expected_unit
    except Exception as e:
        pytest.fail(f"Valid input '{input_str}' raised exception: {e}")


@pytest.mark.parametrize(
    "input_str",
    [
        " ", "five hours", "2 lightyears", "-2 hours", "0 hours", "2.5", "abc"
    ]
)
def test_resolve_human_interval_invalid(input_str):
    """Test invalid intervals produce error."""
    try:
        result = resolve_human_interval.invoke({"interval_str": input_str})
        assert isinstance(result, dict)
        assert "error" in result
    except Exception as e:
        # Pydantic may throw for empty string / whitespace
        assert "Interval string must not be empty" in str(e) or "Invalid" in str(e)


@pytest.mark.parametrize(
    "input_str",
    [
        " 3 days ", "\t2 hours\t", "\n1 week\n"
    ]
)
def test_resolve_human_interval_whitespace(input_str):
    """Test stripping whitespace and normalization."""
    result = resolve_human_interval.invoke({"interval_str": input_str})
    assert "error" not in result
    assert isinstance(result["amount"], float) or isinstance(result["amount"], int)
    assert result["normalized_interval"] in ["hours", "days"]