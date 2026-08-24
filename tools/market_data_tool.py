from typing import Type

import yfinance as yf

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ============================================================
# TOOL INPUT SCHEMA
# ============================================================

class MarketDataInput(BaseModel):
    """Input schema for the Market Data Tool."""

    ticker: str = Field(
        ...,
        description=(
            "The stock ticker symbol of the company. "
            "Examples: AAPL, MSFT, NVDA."
        )
    )


# ============================================================
# HELPER
# ============================================================

def safe_value(value):
    """Convert values into simple Python values."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


# ============================================================
# MARKET DATA TOOL
# ============================================================

class MarketDataTool(BaseTool):

    name: str = "Market Data Tool"

    description: str = (
        "Retrieve current and historical market data for a publicly "
        "traded company. Provides current price, previous close, "
        "52-week range, volume, market capitalization, beta, "
        "dividend yield, and recent historical price performance."
    )

    args_schema: Type[BaseModel] = MarketDataInput

    # --------------------------------------------------------
    # TOOL EXECUTION
    # --------------------------------------------------------

    def _run(self, ticker: str) -> str:

        ticker = ticker.strip().upper()

        if not ticker:
            return "Error: A valid ticker symbol is required."

        try:

            stock = yf.Ticker(ticker)

            info = stock.info
            fast_info = stock.fast_info

            if not info:
                return (
                    f"No market information found for ticker {ticker}."
                )

            # =================================================
            # CURRENT MARKET DATA
            # =================================================

            current_price = safe_value(
                fast_info.get("lastPrice")
            )

            previous_close = safe_value(
                info.get("previousClose")
            )

            day_high = safe_value(
                info.get("dayHigh")
            )

            day_low = safe_value(
                info.get("dayLow")
            )

            week_52_high = safe_value(
                info.get("fiftyTwoWeekHigh")
            )

            week_52_low = safe_value(
                info.get("fiftyTwoWeekLow")
            )

            volume = safe_value(
                info.get("volume")
            )

            average_volume = safe_value(
                info.get("averageVolume")
            )

            market_cap = safe_value(
                info.get("marketCap")
            )

            beta = safe_value(
                info.get("beta")
            )

            dividend_yield = safe_value(
                info.get("dividendYield")
            )

            # =================================================
            # HISTORICAL PRICE DATA
            # =================================================

            history = stock.history(
                period="1mo",
                interval="1d"
            )

            historical_data = []

            if history is not None and not history.empty:

                for date, row in history.tail(10).iterrows():

                    historical_data.append({
                        "date": str(date.date()),
                        "open": safe_value(row.get("Open")),
                        "high": safe_value(row.get("High")),
                        "low": safe_value(row.get("Low")),
                        "close": safe_value(row.get("Close")),
                        "volume": safe_value(row.get("Volume"))
                    })

            # =================================================
            # RESULT
            # =================================================

            result = {
                "source": "Yahoo Finance via yfinance",

                "ticker": ticker,

                "company": (
                    info.get("longName")
                    or info.get("shortName")
                ),

                "market_data": {
                    "current_price": current_price,
                    "previous_close": previous_close,
                    "day_high": day_high,
                    "day_low": day_low,
                    "52_week_high": week_52_high,
                    "52_week_low": week_52_low,
                    "volume": volume,
                    "average_volume": average_volume,
                    "market_cap": market_cap,
                    "beta": beta,
                    "dividend_yield": dividend_yield
                },

                "recent_history": historical_data
            }

            return str(result)

        except Exception as e:

            return (
                f"Unable to retrieve market data for {ticker}. "
                f"Error: {str(e)}"
            )