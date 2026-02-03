# ai/tools/IntervalTools.py
from langchain_core.tools import tool
import re
from typing import Dict, Union

from ai.schemas.time_interval import IntervalParseInput


# ------------------------- Tool -------------------------
@tool(args_schema=IntervalParseInput)
def resolve_human_interval(interval_str: str) -> Union[Dict[str, Union[str, float]], Dict[str, str]]:
    """
    Converts human-friendly interval strings into a normalized amount and unit.

    Normalization rules (compatible with crypto_history API):
        - "hours" for hourly intervals
        - "days" for daily, weekly, monthly intervals
          (weeks = 7 days, months = 30 days)

    Supported units: hours, days, weeks, months
    Examples:
        "2 hours" -> {"amount": 2, "normalized_interval": "hours"}
        "3 weeks" -> {"amount": 21, "normalized_interval": "days"}
        "4 months" -> {"amount": 120, "normalized_interval": "days"}
    """
    interval_str_clean = interval_str.lower().strip()

    # Match number + unit (supports integers and decimals)
    pattern = r"^([\d.]+)\s*(hour|day|week|month)s?$"
    match = re.fullmatch(pattern, interval_str_clean)

    if not match:
        return {"error": f"Invalid interval format: '{interval_str}'"}

    amount_str, unit = match.groups()

    try:
        amount = float(amount_str)
        if amount <= 0:
            return {"error": "Interval amount must be greater than zero"}
    except ValueError:
        return {"error": f"Invalid numeric value: '{amount_str}'"}

    # Normalize units
    if unit == "hour":
        normalized_unit = "hours"
    elif unit == "day":
        normalized_unit = "days"
    elif unit == "week":
        normalized_unit = "days"
        amount *= 7
    elif unit == "month":
        normalized_unit = "days"
        amount *= 30
    else:
        return {"error": f"Unsupported unit: {unit}"}

    return {
        "original": interval_str,
        "amount": amount,
        "normalized_interval": normalized_unit
    }