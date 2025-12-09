import dateparser
from datetime import datetime, timezone

def resolve_date(date_str: str) -> str:
    """
    Convert relative or natural language dates into YYYY-MM-DD format in UTC.
    """
    # FIX 1: Use a naive datetime for RELATIVE_BASE (dateparser best practice)
    # This resolves the 'last Friday' failure.
    base_naive = datetime.now()

    if not date_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    dt = dateparser.parse(
        date_str,
        settings={
            "RELATIVE_BASE": base_naive, # Use naive base
            "TIMEZONE": "UTC",
            "TO_TIMEZONE": "UTC",
            "PREFER_DATES_FROM": "past",
            "RETURN_AS_TIMEZONE_AWARE": True,
            # FIX 2: Explicitly prefer the last day of the month for incomplete dates
            "PREFER_DAY_OF_MONTH": "last"
        },
        languages=["en"]
    )

    if not dt:
        # A failed parse should ideally return None or raise an error (as discussed previously)
        # but maintaining the original logic to return today's date on failure:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return dt.strftime("%Y-%m-%d")

