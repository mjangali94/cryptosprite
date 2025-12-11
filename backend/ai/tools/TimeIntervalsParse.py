from pydantic import BaseModel, Field
from langchain_core.tools import tool
import re

class IntervalParseInput(BaseModel):
    interval_str: str = Field(..., description="Human-friendly interval (e.g., '2.5 hours', '3 weeks', '4 months')")

@tool(args_schema=IntervalParseInput)
def resolve_human_interval(interval_str: str):
    """
    Converts human-friendly interval strings to (amount, normalized_interval)
    Compatible with your existing crypto_history API.
    """
    interval_str = interval_str.lower().strip()
    pattern = r"([\d\.]+)\s*(hour|day|week|month|hours|days|weeks|months)"
    match = re.match(pattern, interval_str)

    if not match:
        return {"error": f"Invalid interval format: '{interval_str}'"}

    amount, unit = match.groups()
    amount = float(amount)

    # Normalize
    if unit.startswith("hour"):
        normalized_unit = "hours"
    elif unit.startswith("day"):
        normalized_unit = "days"
    elif unit.startswith("week"):
        normalized_unit = "days"
        amount = amount * 7
    elif unit.startswith("month"):
        normalized_unit = "days"
        amount = amount * 30
    else:
        return {"error": f"Unsupported unit: {unit}"}

    return {
        "original": interval_str,
        "amount": amount,
        "normalized_interval": normalized_unit
    }