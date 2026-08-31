from typing import Type
import os

import requests

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ============================================================
# INPUT SCHEMA
# ============================================================

class SECFinancialInput(BaseModel):
    """Input schema for SEC Financial Data Tool."""

    ticker: str = Field(
        ...,
        description=(
            "US publicly traded company ticker symbol. "
            "Examples: AAPL, MSFT, NVDA."
        )
    )


# ============================================================
# SEC TOOL
# ============================================================

class SECFinancialDataTool(BaseTool):

    name: str = "SEC Financial Data Tool"

    description: str = (
        "Retrieve official financial statement data from the U.S. "
        "SEC EDGAR XBRL Company Facts API for a US publicly traded "
        "company. Use this tool for verified revenue, net income, "
        "assets, liabilities, cash, equity, debt, and cash-flow "
        "information."
    )

    args_schema: Type[BaseModel] = SECFinancialInput

    # ========================================================
    # SEC CIK LOOKUP
    # ========================================================

    def _get_company_tickers(self):

        url = (
            "https://www.sec.gov/files/"
            "company_tickers.json"
        )

        headers = {
            "User-Agent": os.getenv(
                "SEC_USER_AGENT",
                "AIInvestmentResearch contact@example.com"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        return response.json()

    # ========================================================
    # FIND CIK
    # ========================================================

    def _get_cik(self, ticker):

        ticker = ticker.upper()

        companies = self._get_company_tickers()

        for company in companies.values():

            if company["ticker"].upper() == ticker:

                return str(
                    company["cik_str"]
                ).zfill(10)

        return None

    # ========================================================
    # COMPANY FACTS
    # ========================================================

    def _get_company_facts(self, cik):

        url = (
            f"https://data.sec.gov/api/xbrl/"
            f"companyfacts/CIK{cik}.json"
        )

        headers = {
            "User-Agent": os.getenv(
                "SEC_USER_AGENT",
                "AIInvestmentResearch contact@example.com"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    # ========================================================
    # EXTRACT FACT
    # ========================================================

    def _extract_fact(
        self,
        facts,
        taxonomy,
        concepts,
        unit="USD"
    ):

        taxonomy_data = facts.get(
            "facts",
            {}
        ).get(
            taxonomy,
            {}
        )

        for concept in concepts:

            if concept not in taxonomy_data:
                continue

            units = taxonomy_data[
                concept
            ].get(
                "units",
                {}
            )

            values = units.get(unit)

            if not values:
                continue

            # Get recent annual 10-K facts first
            annual_values = [
                item
                for item in values
                if item.get("form") == "10-K"
            ]

            if annual_values:
                values = annual_values

            # Sort by filing date
            values = sorted(
                values,
                key=lambda x: x.get(
                    "filed",
                    ""
                )
            )

            # Return most recently filed value
            latest = values[-1]

            return {
                "concept": concept,
                "value": latest.get("val"),
                "unit": unit,
                "filed": latest.get("filed"),
                "form": latest.get("form"),
                "fy": latest.get("fy"),
                "fp": latest.get("fp"),
                "start": latest.get("start"),
                "end": latest.get("end")
            }

        return None

    # ========================================================
    # EXTRACT HISTORICAL FACTS
    # ========================================================

    def _extract_historical_fact(
        self,
        facts,
        taxonomy,
        concepts,
        unit="USD",
        limit=5
    ):
        taxonomy_data = facts.get("facts", {}).get(taxonomy, {})

        for concept in concepts:
            if concept not in taxonomy_data:
                continue

            units = taxonomy_data[concept].get("units", {})
            values = units.get(unit)

            if not values:
                continue

            # Get annual 10-K facts first
            annual_values = [
                item for item in values if item.get("form") == "10-K" and item.get("fy") is not None
            ]

            if not annual_values:
                continue

            # Sort by fiscal year and filing date (to get the latest revision for each year)
            annual_values = sorted(
                annual_values,
                key=lambda x: (x.get("fy"), x.get("filed", ""))
            )

            # Deduplicate by fiscal year (take the latest filed value for each year)
            fy_dict = {}
            for item in annual_values:
                fy_dict[item.get("fy")] = {
                    "fy": item.get("fy"),
                    "value": item.get("val"),
                    "unit": unit,
                    "form": item.get("form"),
                    "filed": item.get("filed"),
                    "start": item.get("start"),
                    "end": item.get("end")
                }

            # Sort fiscal years ascending
            sorted_fys = sorted(list(fy_dict.keys()))

            # Take up to the last `limit` years
            recent_fys = sorted_fys[-limit:]

            history = [fy_dict[fy] for fy in recent_fys]

            if history:
                return history

        return []

    # ========================================================
    # TOOL EXECUTION
    # ========================================================

    def get_financial_data(self, ticker: str):
        """
        Retrieve structured SEC financial data for internal Python use.
        CrewAI calls _run(), which keeps returning a string-compatible
        representation for the tool interface.
        """

        ticker = ticker.strip().upper()

        try:

            # ------------------------------------------------
            # CIK
            # ------------------------------------------------

            cik = self._get_cik(ticker)

            if not cik:

                return (
                    f"Could not find SEC CIK for "
                    f"ticker {ticker}."
                )

            # ------------------------------------------------
            # COMPANY FACTS
            # ------------------------------------------------

            facts = self._get_company_facts(cik)

            company_name = facts.get(
                "entityName"
            )

            # ------------------------------------------------
            # FINANCIAL FACTS
            # ------------------------------------------------

            revenue = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "RevenueFromContractWithCustomerExcludingAssessedTax",
                    "Revenues"
                ]
            )

            net_income = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "NetIncomeLoss"
                ]
            )

            gross_profit = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "GrossProfit"
                ]
            )

            operating_income = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "OperatingIncomeLoss"
                ]
            )

            assets = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "Assets"
                ]
            )

            liabilities = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "Liabilities"
                ]
            )

            equity = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "StockholdersEquity"
                ]
            )

            cash = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "CashAndCashEquivalentsAtCarryingValue"
                ]
            )

            # ------------------------------------------------
            # DEBT
            # ------------------------------------------------

            current_debt = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "LongTermDebtCurrent"
                ]
            )

            non_current_debt = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "LongTermDebtNoncurrent"
                ]
            )

            operating_cash_flow = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "NetCashProvidedByUsedInOperatingActivities"
                ]
            )

            capital_expenditure = self._extract_fact(
                facts,
                "us-gaap",
                [
                    "PaymentsToAcquirePropertyPlantAndEquipment"
                ]
            )

            total_debt = self._combine_debt(
                current_debt,
                non_current_debt
            )

            # ------------------------------------------------
            # HISTORICAL FACTS (UP TO 5 YEARS)
            # ------------------------------------------------
            
            hist_revenue = self._extract_historical_fact(facts, "us-gaap", ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"])
            hist_net_income = self._extract_historical_fact(facts, "us-gaap", ["NetIncomeLoss"])
            hist_gross_profit = self._extract_historical_fact(facts, "us-gaap", ["GrossProfit"])
            hist_operating_income = self._extract_historical_fact(facts, "us-gaap", ["OperatingIncomeLoss"])
            hist_assets = self._extract_historical_fact(facts, "us-gaap", ["Assets"])
            hist_liabilities = self._extract_historical_fact(facts, "us-gaap", ["Liabilities"])
            hist_equity = self._extract_historical_fact(facts, "us-gaap", ["StockholdersEquity"])
            hist_cash = self._extract_historical_fact(facts, "us-gaap", ["CashAndCashEquivalentsAtCarryingValue"])
            
            # For debt, we need to extract current and non-current separately and combine them if possible
            hist_current_debt = self._extract_historical_fact(facts, "us-gaap", ["LongTermDebtCurrent"])
            hist_non_current_debt = self._extract_historical_fact(facts, "us-gaap", ["LongTermDebtNoncurrent"])
            hist_operating_cash_flow = self._extract_historical_fact(facts, "us-gaap", ["NetCashProvidedByUsedInOperatingActivities"])
            hist_capital_expenditure = self._extract_historical_fact(facts, "us-gaap", ["PaymentsToAcquirePropertyPlantAndEquipment"])
            
            # Build combined historical debt if both exist for a given fy
            hist_total_debt = []
            cur_map = {item["fy"]: item for item in hist_current_debt}
            non_cur_map = {item["fy"]: item for item in hist_non_current_debt}
            
            for fy in sorted(set(list(cur_map.keys()) + list(non_cur_map.keys()))):
                c_item = cur_map.get(fy)
                nc_item = non_cur_map.get(fy)
                if c_item is not None and nc_item is not None:
                    base = c_item if (c_item.get("filed") or "") > (nc_item.get("filed") or "") else nc_item
                    hist_total_debt.append({
                        "fy": fy,
                        "value": c_item["value"] + nc_item["value"],
                        "unit": base.get("unit"),
                        "form": base.get("form"),
                        "filed": base.get("filed"),
                        "start": base.get("start"),
                        "end": base.get("end")
                    })

            historical_financials = {
                "revenue": hist_revenue,
                "gross_profit": hist_gross_profit,
                "operating_income": hist_operating_income,
                "net_income": hist_net_income,
                "assets": hist_assets,
                "liabilities": hist_liabilities,
                "equity": hist_equity,
                "cash": hist_cash,
                "total_debt": hist_total_debt,
                "operating_cash_flow": hist_operating_cash_flow,
                "capital_expenditure": [{**item, "value": -abs(item["value"])} for item in hist_capital_expenditure]
            }

            # ========================================================
            # NORMALIZED FINANCIAL DATA
            # ========================================================

            normalized_financial_data = {
                "revenue": (
                    revenue.get("value")
                    if revenue
                    else None
                ),

                "gross_profit": (
                    gross_profit.get("value")
                    if gross_profit
                    else None
                ),

                "operating_income": (
                    operating_income.get("value")
                    if operating_income
                    else None
                ),

                "net_income": (
                    net_income.get("value")
                    if net_income
                    else None
                ),

                "assets": (
                    assets.get("value")
                    if assets
                    else None
                ),

                "liabilities": (
                    liabilities.get("value")
                    if liabilities
                    else None
                ),

                "stockholders_equity": (
                    equity.get("value")
                    if equity
                    else None
                ),

                "cash": (
                    cash.get("value")
                    if cash
                    else None
                ),

                "total_debt": (
                    total_debt.get("value")
                    if total_debt
                    else None
                ),

                "operating_cash_flow": (
                    operating_cash_flow.get("value")
                    if operating_cash_flow
                    else None
                ),

                "capital_expenditure": (
                    -abs(capital_expenditure.get("value"))
                    if capital_expenditure
                    else None
                )
            }

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            raw_financial_data = {

                "revenue": revenue,

                "gross_profit": gross_profit,

                "operating_income": operating_income,

                "net_income": net_income,

                "assets": assets,

                "liabilities": liabilities,

                "stockholders_equity": equity,

                "cash_and_equivalents": cash,

                "debt": {
                    "current": current_debt,
                    "non_current": non_current_debt,
                    "total": total_debt
                },

                "operating_cash_flow": operating_cash_flow,

                "capital_expenditure": capital_expenditure
            }

            reporting_metadata = {
                "cik": cik,
                "form": (
                    revenue.get("form")
                    if revenue
                    else None
                ),
                "fiscal_year": (
                    revenue.get("fy")
                    if revenue
                    else None
                ),
                "fiscal_period": (
                    revenue.get("fp")
                    if revenue
                    else None
                ),
                "filed": (
                    revenue.get("filed")
                    if revenue
                    else None
                ),
                "period_start": (
                    revenue.get("start")
                    if revenue
                    else None
                ),
                "period_end": (
                    revenue.get("end")
                    if revenue
                    else None
                )
            }

            result = {

                "source": "SEC EDGAR XBRL Company Facts API",

                "ticker": ticker,

                "cik": cik,

                "company": company_name,

                "reporting_metadata": reporting_metadata,

                "financial_data": {
                    **raw_financial_data,
                    "raw": raw_financial_data,
                    "normalized": normalized_financial_data,
                    "historical": historical_financials
                }

            }

            return result

        except requests.RequestException as e:

            return (
                "SEC API request failed: "
                f"{str(e)}"
            )

        except Exception as e:

            return (
                "Unable to retrieve SEC financial "
                f"data for {ticker}: {str(e)}"
            )

    def _run(self, ticker: str) -> str:

        return str(
            self.get_financial_data(
                ticker=ticker
            )
        )

    def _combine_debt(
        self,
        current_debt,
        non_current_debt
    ):
        """
        Combine current and non-current debt only when
        both values are available from the same reporting
        period.
        """

        if not current_debt or not non_current_debt:
            return None

        if current_debt.get("unit") != "USD":
            return None

        if non_current_debt.get("unit") != "USD":
            return None

        current_value = current_debt.get("value")
        non_current_value = non_current_debt.get("value")

        if current_value is None or non_current_value is None:
            return None

        if current_debt.get("end") != non_current_debt.get("end"):
            return None

        if current_debt.get("form") != non_current_debt.get("form"):
            return None

        if current_debt.get("fy") != non_current_debt.get("fy"):
            return None

        return {
            "value": current_value + non_current_value,
            "unit": "USD",
            "current_debt": current_debt,
            "non_current_debt": non_current_debt,
            "period_end": current_debt.get("end"),
            "form": current_debt.get("form"),
            "fy": current_debt.get("fy")
        }
