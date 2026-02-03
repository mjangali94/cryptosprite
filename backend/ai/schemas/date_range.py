from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
import re


class TodayDateInput(BaseModel):
    """
    Input model for fetching today's date.

    This is a placeholder model, useful for consistency in API endpoints
    that always expect a structured input, even if no parameters are required.
    """
    pass


class DateParseInput(BaseModel):
    """
    Input model for parsing human-friendly dates or date ranges.

    Supports:
    - Single dates: '2025-01-01', 'today', 'yesterday'
    - Relative dates: '2 days ago', '3 weeks ago'
    - Ranges: 'last 7 days', 'last month'
    """
    date_str: str = Field(
        ...,
        description=(
            "Human-friendly date or date range "
            "(e.g., 'yesterday', '2 weeks ago', 'last month', '2025-01-01')"
        ),
        example="yesterday"
    )
    output_format: Optional[str] = Field(
        default="%Y-%m-%d",
        description="Optional format string for the returned date (Python strftime format).",
        example="%Y-%m-%d"
    )

    @validator("date_str")
    def validate_date_str(cls, v: str) -> str:
        """Basic sanity check for input string."""
        if not v or not isinstance(v, str):
            raise ValueError("date_str must be a non-empty string")
        if len(v) > 100:
            raise ValueError("date_str is too long")
        return v

    @validator("output_format")
    def validate_output_format(cls, v: str) -> str:
        """Ensure output_format is a valid strftime format."""
        try:
            datetime.now().strftime(v)
        except Exception:
            raise ValueError(f"Invalid output_format: {v}")
        return v

    def is_relative_date(self) -> bool:
        """Check if the input is a relative date like '2 days ago'."""
        return bool(re.search(r"(ago|last|yesterday|today|week|month|year)", self.date_str.lower()))

    def parse_as_datetime(self) -> datetime:
        """
        Attempt to convert the date_str into a datetime object.

        For now, supports:
        - 'today', 'yesterday'
        - ISO dates like 'YYYY-MM-DD'
        - Future support for relative parsing (2 days ago, last week)
        """
        lower = self.date_str.lower()
        if lower == "today":
            return datetime.now()
        if lower == "yesterday":
            return datetime.now() - timedelta(days=1)
        # Try ISO date
        try:
            return datetime.strptime(self.date_str, "%Y-%m-%d")
        except ValueError:
            pass
        # Future: extend with dateparser, parsedatetime, or custom logic
        raise ValueError(f"Unable to parse date string: {self.date_str}")