from typing import Type
import math

import yfinance as yf

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ============================================================
# INPUT SCHEMA
# ============================================================

class FinancialDataInput(BaseModel):
    """Input schema for the Financial Data Tool."""

    ticker: str = Field(
        ...,
        description=(
            "Stock ticker symbol of the publicly traded company. "
            "Examples: AAPL, MSFT, NVDA."
        )
    )


# ============================================================
# HELPERS
# ============================================================

def clean_value(value):
    """
    Convert pandas/numpy values into JSON-safe Python values.
    """

    if value is None:
        return None

    try:
        if isinstance(value, float) and math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass

    try: