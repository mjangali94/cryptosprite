from pydantic import BaseModel, Field
from langchain_core.tools import tool
from datetime import datetime, timedelta
import re
import dateparser


class TodayDateInput(BaseModel):
    """No input needed for this tool."""
    dummy: str = Field("", description="Just a placeholder field")

@tool(args_schema=TodayDateInput)
def get_today_date(dummy: str = "") -> str:
    """
    Returns today's date in YYYY-MM-DD format.
    """
    return datetime.today().strftime("%Y-%m-%d")


class DateParseInput(BaseModel):
    date_str: str = Field(..., description="Human-friendly date or date range (e.g., 'yesterday', '2 weeks ago', 'last month', '2025-01-01')")

@tool(args_schema=DateParseInput)
def resolve_date_range(date_str: str):
    """
    Converts human-friendly relative dates (like 'today', '2 weeks ago', 'last 3 days', '2025-01-01')
    into actual ISO dates (YYYY-MM-DD). Can return a list of dates for ranges.
    """
    date_str_lower = date_str.lower().strip()
    today = datetime.today().date()

    # Check for keywords anywhere in the string
    if "today" in date_str_lower:
        return {"original": date_str, "dates": [today.isoformat()]}
    if "yesterday" in date_str_lower:
        return {"original": date_str, "dates": [(today - timedelta(days=1)).isoformat()]}

    # Match "X days/weeks/months ago"
    match = re.search(r"(\d+)\s*(day|week|month)s?\s*ago", date_str_lower)
    if match:
        amount, unit = match.groups()
        amount = int(amount)
        if unit == "day":
            target_date = today - timedelta(days=amount)
        elif unit == "week":
            target_date = today - timedelta(weeks=amount)
        elif unit == "month":
            target_date = today - timedelta(days=amount*30)
        return {"original": date_str, "dates": [target_date.isoformat()]}

    # Match explicit ranges: "last X days/weeks/months"
    match_range = re.search(r"last\s+(\d+)\s*(day|week|month)s?", date_str_lower)
    if match_range:
        amount, unit = match_range.groups()
        amount = int(amount)
        if unit == "day":
            start_date = today - timedelta(days=amount-1)
        elif unit == "week":
            start_date = today - timedelta(weeks=amount)
        elif unit == "month":
            start_date = today - timedelta(days=amount*30)
        date_list = [(start_date + timedelta(days=i)).isoformat() for i in range((today - start_date).days + 1)]
        return {"original": date_str, "dates": date_list}

    # Try parsing absolute dates anywhere in the string using dateparser
    dt = dateparser.parse(date_str)
    if dt:
        return {"original": date_str, "dates": [dt.date().isoformat()]}

    return {"error": f"Could not parse date string: '{date_str}'"}