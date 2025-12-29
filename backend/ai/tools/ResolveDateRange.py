from pydantic import BaseModel, Field
from langchain_core.tools import tool
from datetime import datetime, timedelta
import re
import dateparser
from typing import List, Dict, Union


# ------------------------- Schemas -------------------------
class TodayDateInput(BaseModel):
    """Optional placeholder input for getting today's date."""
    pass


class DateParseInput(BaseModel):
    date_str: str = Field(
        ...,
        description="Human-friendly date or date range "
                    "(e.g., 'yesterday', '2 weeks ago', 'last month', '2025-01-01')"
    )


# ------------------------- Tools -------------------------
@tool(args_schema=TodayDateInput)
def get_today_date() -> str:
    """
    Returns today's date in YYYY-MM-DD format.
    """
    return datetime.today().strftime("%Y-%m-%d")


@tool(args_schema=DateParseInput)
def resolve_date_range(date_str: str) -> Union[Dict[str, List[str]], Dict[str, str]]:
    """
    Converts human-friendly relative dates (like 'today', '2 weeks ago', 'last 3 days', '2025-01-01')
    into actual ISO dates (YYYY-MM-DD). Can return a list of dates for ranges.
    """
    date_str_lower = date_str.lower().strip()
    today = datetime.today().date()

    def generate_past_dates(amount: int, unit: str) -> List[str]:
        """Generates a list of past dates including today."""
        if unit == "day":
            start_date = today - timedelta(days=amount-1)
            return [(start_date + timedelta(days=i)).isoformat() for i in range(amount)]
        elif unit == "week":
            start_date = today - timedelta(weeks=amount)
            return [(start_date + timedelta(days=i)).isoformat() for i in range((today - start_date).days + 1)]
        elif unit == "month":
            start_date = today - timedelta(days=amount*30)
            return [(start_date + timedelta(days=i)).isoformat() for i in range((today - start_date).days + 1)]
        return []

    # Keywords: today, yesterday
    if "today" in date_str_lower:
        return {"original": date_str, "dates": [today.isoformat()]}
    if "yesterday" in date_str_lower:
        return {"original": date_str, "dates": [(today - timedelta(days=1)).isoformat()]}

    # Relative past: "X days/weeks/months ago"
    match_ago = re.search(r"(\d+)\s*(day|week|month)s?\s*ago", date_str_lower)
    if match_ago:
        amount, unit = match_ago.groups()
        target_date = today - timedelta(days=int(amount) * (30 if unit == "month" else 7 if unit == "week" else 1))
        return {"original": date_str, "dates": [target_date.isoformat()]}

    # Relative range: "last X days/weeks/months"
    match_last = re.search(r"last\s+(\d+)\s*(day|week|month)s?", date_str_lower)
    if match_last:
        amount, unit = match_last.groups()
        dates_list = generate_past_dates(int(amount), unit)
        return {"original": date_str, "dates": dates_list}

    # Attempt absolute date parsing
    dt = dateparser.parse(date_str)
    if dt:
        return {"original": date_str, "dates": [dt.date().isoformat()]}

    return {"error": f"Could not parse date string: '{date_str}'"}
