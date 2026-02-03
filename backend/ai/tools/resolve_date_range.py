# ai/tools/DateTools.py
from langchain_core.tools import tool
from datetime import datetime, timedelta
import re
import dateparser
from typing import List, Dict, Union

from ai.schemas.date_range import TodayDateInput, DateParseInput


# ------------------------- Tools -------------------------
@tool(args_schema=TodayDateInput)
def get_today_date() -> str:
    """
    Returns today's date in ISO format (YYYY-MM-DD).

    Example:
        >>> get_today_date()
        '2026-02-02'
    """
    return datetime.today().strftime("%Y-%m-%d")


@tool(args_schema=DateParseInput)
def resolve_date_range(date_str: str) -> Union[Dict[str, List[str]], Dict[str, str]]:
    """
    Converts human-friendly date strings into actual ISO dates (YYYY-MM-DD).

    Supports:
    - Single keywords: 'today', 'yesterday'
    - Relative past: '2 days ago', '3 weeks ago', '1 month ago'
    - Relative range: 'last 7 days', 'last 3 weeks', 'last 2 months'
    - Absolute dates: '2025-01-01'

    Returns:
        Dict[str, List[str]]: For successful parsing, includes the original string and list of dates.
        Dict[str, str]: If parsing fails, returns an error message.

    Examples:
        >>> resolve_date_range("today")
        {'original': 'today', 'dates': ['2026-02-02']}

        >>> resolve_date_range("last 3 days")
        {'original': 'last 3 days', 'dates': ['2026-01-31', '2026-02-01', '2026-02-02']}

        >>> resolve_date_range("2025-01-01")
        {'original': '2025-01-01', 'dates': ['2025-01-01']}
    """
    date_str_lower = date_str.lower().strip()
    today = datetime.today().date()

    def generate_past_dates(amount: int, unit: str) -> List[str]:
        """Generate list of past dates including today for ranges."""
        if unit == "day":
            start_date = today - timedelta(days=amount - 1)
        elif unit == "week":
            start_date = today - timedelta(weeks=amount - 1)
        elif unit == "month":
            # Approximate month as 30 days
            start_date = today - timedelta(days=30 * (amount - 1))
        else:
            return []

        num_days = (today - start_date).days + 1
        return [(start_date + timedelta(days=i)).isoformat() for i in range(num_days)]

    # Handle single keywords
    if date_str_lower == "today":
        return {"original": date_str, "dates": [today.isoformat()]}
    if date_str_lower == "yesterday":
        return {"original": date_str, "dates": [(today - timedelta(days=1)).isoformat()]}

    # Handle relative past: "X days/weeks/months ago"
    match_ago = re.search(r"(\d+)\s*(day|week|month)s?\s*ago", date_str_lower)
    if match_ago:
        amount, unit = match_ago.groups()
        delta_days = int(amount) * (30 if unit == "month" else 7 if unit == "week" else 1)
        target_date = today - timedelta(days=delta_days)
        return {"original": date_str, "dates": [target_date.isoformat()]}

    # Handle relative ranges: "last X days/weeks/months"
    match_last = re.search(r"last\s+(\d+)\s*(day|week|month)s?", date_str_lower)
    if match_last:
        amount, unit = match_last.groups()
        dates_list = generate_past_dates(int(amount), unit)
        return {"original": date_str, "dates": dates_list}

    # Attempt absolute date parsing
    dt = dateparser.parse(date_str)
    if dt:
        return {"original": date_str, "dates": [dt.date().isoformat()]}

    # Return error if parsing failed
    return {"error": f"Could not parse date string: '{date_str}'"}