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
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def extract_statement(statement, metrics):
    """
    Extract selected financial metrics from a yfinance
    financial statement.
    """

    result = {}

    if statement is None or statement.empty:
        return result

    for metric in metrics:

        if metric not in statement.index:
            continue

        values = statement.loc[metric]

        metric_data = {}

        for date, value in values.items():

            cleaned = clean_value(value)

            if cleaned is not None:
                metric_data[str(date)] = cleaned

        if metric_data:
            result[metric] = metric_data

    return result


# ============================================================
# FINANCIAL DATA TOOL
# ============================================================

class FinancialDataTool(BaseTool):

    name: str = "Financial Data Tool"

    description: str = (
        "Retrieve fundamental financial information for a publicly "
        "traded company using its stock ticker. The tool retrieves "
        "income statement, balance sheet, cash flow, and important "
        "financial metrics. Use this tool before making claims about "
        "financial numbers."
    )

    args_schema: Type[BaseModel] = FinancialDataInput

    # ========================================================
    # TOOL EXECUTION
    # ========================================================

    def _run(self, ticker: str) -> str:

        ticker = ticker.strip().upper()

        if not ticker:
            return "Error: A valid stock ticker is required."

        try:

            stock = yf.Ticker(ticker)

            # =================================================
            # COMPANY INFORMATION
            # =================================================

            info = {}

            try:
                info = stock.info
            except Exception:
                info = {}

            company_name = (
                info.get("longName")
                or info.get("shortName")
            )

            sector = info.get("sector")
            industry = info.get("industry")
            country = info.get("country")

            # =================================================
            # INCOME STATEMENT
            # =================================================

            income_statement = None

            try:
                income_statement = stock.get_income_stmt(
                    freq="yearly"
                )
            except Exception:
                try:
                    income_statement = stock.income_stmt
                except Exception:
                    income_statement = None

            income_metrics = [
                "Total Revenue",
                "Gross Profit",
                "Operating Income",
                "Net Income",
                "Diluted EPS",
                "Basic EPS"
            ]

            income_data = extract_statement(
                income_statement,
                income_metrics
            )

            # =================================================
            # BALANCE SHEET
            # =================================================

            balance_sheet = None

            try:
                balance_sheet = stock.get_balance_sheet(
                    freq="yearly"
                )
            except Exception:
                try:
                    balance_sheet = stock.balance_sheet
                except Exception:
                    balance_sheet = None

            balance_metrics = [
                "Cash And Cash Equivalents",
                "Cash Cash Equivalents And Short Term Investments",
                "Total Assets",
                "Total Liabilities Net Minority Interest",
                "Stockholders Equity",
                "Total Debt",
                "Current Assets",
                "Current Liabilities"
            ]

            balance_data = extract_statement(
                balance_sheet,
                balance_metrics
            )

            # =================================================
            # CASH FLOW STATEMENT
            # =================================================

            cash_flow = None

            try:
                cash_flow = stock.get_cash_flow(
                    freq="yearly"
                )
            except Exception:
                try:
                    cash_flow = stock.cashflow
                except Exception:
                    cash_flow = None

            cash_flow_metrics = [
                "Operating Cash Flow",
                "Free Cash Flow",
                "Capital Expenditure",
                "Repurchase Of Capital Stock",
                "Cash Dividends Paid"
            ]

            cash_flow_data = extract_statement(
                cash_flow,
                cash_flow_metrics
            )

            # =================================================
            # VALUATION METRICS
            # =================================================

            valuation_data = {
                "Market Cap": clean_value(
                    info.get("marketCap")
                ),

                "Trailing P/E": clean_value(
                    info.get("trailingPE")
                ),

                "Forward P/E": clean_value(
                    info.get("forwardPE")
                ),

                "Price To Sales": clean_value(
                    info.get(
                        "priceToSalesTrailing12Months"
                    )
                ),

                "Price To Book": clean_value(
                    info.get("priceToBook")
                ),

                "Enterprise Value": clean_value(
                    info.get("enterpriseValue")
                ),

                "Enterprise To EBITDA": clean_value(
                    info.get("enterpriseToEbitda")
                )
            }

            # =================================================
            # DATA AVAILABILITY STATUS
            # =================================================

            statement_status = {
                "income_statement": (
                    "available"
                    if income_data
                    else "unavailable"
                ),

                "balance_sheet": (
                    "available"
                    if balance_data
                    else "unavailable"
                ),

                "cash_flow": (
                    "available"
                    if cash_flow_data
                    else "unavailable"
                )
            }

            # =================================================
            # FINAL RESULT
            # =================================================

            result = {
                "source": "Yahoo Finance via yfinance",

                "ticker": ticker,

                "company": company_name,

                "sector": sector,

                "industry": industry,

                "country": country,

                "valuation_metrics": valuation_data,

                "income_statement": income_data,

                "balance_sheet": balance_data,

                "cash_flow": cash_flow_data,

                "data_availability": statement_status
            }

            return str(result)

        except Exception as e:

            return (
                f"Unable to retrieve financial data for {ticker}. "
                f"Error: {str(e)}"
            )