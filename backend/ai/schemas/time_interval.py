# ai/schemas/interval.py
from pydantic import BaseModel, Field, condecimal, validator
from typing import Literal


class IntervalParseInput(BaseModel):
    """
    Schema for parsing human-friendly time intervals into seconds.
    Example inputs: '2 hours', '3 weeks', '4 months', '2.5 hours'
    """
    interval_str: str = Field(
        ...,
        min_length=1,
        description=(
            "Human-friendly interval string. "
            "Examples: '2 hours', '90 minutes', '3 weeks', '1 month', '2.5 hours'"
        )
    )

    unit: Literal["seconds", "minutes", "hours", "days", "weeks", "months"] | None = Field(
        None,
        description=(
            "Optional: specify the unit to normalize to. "
            "Defaults to seconds if not provided."
        )
    )

    multiplier: condecimal(gt=0) | None = Field(
        None,
        description=(
            "Optional: numeric multiplier to override parsing. "
            "Useful for testing or fixed intervals."
        )
    )

    @validator("interval_str")
    def validate_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Interval string must not be empty")
        return v.strip()