from pydantic import BaseModel, Field, conlist, PositiveInt, PositiveFloat
from typing import List


# -------------------------
# Market / Price Tools Inputs
# -------------------------
class MarketSummaryInput(BaseModel):
    symbols: conlist(str, min_length=1) = Field(..., description="List of cryptocurrency symbols (e.g., ['BTC', 'ETH'])")
    interval: str = Field("days", description="Time interval for data aggregation ('hours', 'days', 'months')")
    amount: PositiveInt = Field(7, description="Number of intervals to fetch")


class TopMoversInput(BaseModel):
    symbols: conlist(str, min_length=1) = Field(..., description="List of cryptocurrency symbols to analyze for top movers")
    interval: str = Field("days", description="Time interval for price comparison")
    amount: PositiveInt = Field(7, description="Number of intervals to fetch")


class PriceVolumeCorrelationInput(BaseModel):
    symbol: str = Field(..., description="Single cryptocurrency symbol to analyze price-volume correlation")
    interval: str = Field("days", description="Time interval for data aggregation")
    amount: PositiveInt = Field(7, description="Number of intervals to fetch")


class PercentageChangeAlertInput(BaseModel):
    symbols: conlist(str, min_length=1) = Field(..., description="Cryptocurrency symbols to monitor for significant price changes")
    threshold: PositiveFloat = Field(5.0, description="Percentage change threshold to trigger alerts")
    interval: str = Field("days", description="Time interval for price comparison")
    amount: PositiveInt = Field(7, description="Number of intervals to fetch")


class VolatilityOverviewInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol to analyze volatility")
    interval: str = Field("days", description="Time interval for volatility calculation")
    amount: PositiveInt = Field(7, description="Number of intervals to fetch")


class MovingAverageInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol to compute moving averages for")
    short_term: PositiveInt = Field(7, description="Short-term moving average period")
    mid_term: PositiveInt = Field(14, description="Mid-term moving average period")
    interval: str = Field("days", description="Time interval for moving average calculation")


class HistoricalPerformanceInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol to analyze historical performance")
    intervals: conlist(str, min_length=1) = Field(["hours", "days", "months"], description="List of intervals to evaluate (e.g., ['hours', 'days', 'months'])")
    amounts: conlist(PositiveInt, min_length=1) = Field([12, 14, 12], description="Number of periods to fetch for each interval; must match length of intervals")


class CoinComparisonInput(BaseModel):
    symbols: conlist(str, min_length=1) = Field(..., description="List of cryptocurrency symbols to compare")
    interval: str = Field("days", description="Time interval for price/volume/trend comparison")
    amount: PositiveInt = Field(7, description="Number of intervals to fetch")


from pydantic import BaseModel, Field

class RSIInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC' or 'ETH'")
    interval: str = Field("days", description="Time interval for historical data ('hours', 'days', 'months')")
    amount: int = Field(14, description="Number of periods to calculate RSI (typical RSI period is 14)")

class MACDInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC'")
    short_term: int = Field(12, description="Short-term period for MACD calculation")
    long_term: int = Field(26, description="Long-term period for MACD calculation")
    signal: int = Field(9, description="Signal line period for MACD")
    interval: str = Field("days", description="Time interval for historical data ('hours', 'days', 'months')")

class BollingerBandsInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC'")
    period: int = Field(20, description="Number of periods to calculate the moving average")
    interval: str = Field("days", description="Time interval for historical data ('hours', 'days', 'months')")
    std_dev_multiplier: float = Field(2.0, description="Number of standard deviations for upper/lower bands")

class PriceTrendInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC'")
    interval: str = Field("days", description="Time interval for historical data ('hours', 'days', 'months')")
    amount: int = Field(7, description="Number of intervals to evaluate the trend")

class EMAInput(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol, e.g., 'BTC'")
    period: int = Field(14, description="Number of periods for EMA calculation")
    interval: str = Field("days", description="Time interval for historical data ('hours', 'days', 'months')")