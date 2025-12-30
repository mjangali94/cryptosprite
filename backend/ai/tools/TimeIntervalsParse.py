from pydantic import BaseModel, Field
from langchain_core.tools import tool
import re

class IntervalParseInput(BaseModel):
    interval_str: str = Field(..., description="Human-friendly interval (e.g., '2.5 hours', '3 weeks', '4 months')")

@tool(args_schema=IntervalParseInput)
def resolve_human_interval(interval_str: str):
    """
    Converts human-friendly interval strings to (amount, normalized_interval)
    Normalizes to hours or days. Compatible with your existing crypto_history API.
    """
    interval_str = interval_str.lower().strip()
    
    # Match number + unit
    pattern = r"([\d.]+)\s*(hour|day|week|month)s?"
    match = re.fullmatch(pattern, interval_str)
    
    if not match:
        return {"error": f"Invalid interval format: '{interval_str}'"}
    
    amount, unit = match.groups()
    amount = float(amount)

    # Normalize to standard units
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
