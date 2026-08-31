"""
investment_research_report.py
─────────────────────────────
Phase 3.6 – Final Structured Investment Research Report

Defines the canonical `InvestmentResearchReport` Pydantic model that
assembles the complete research pipeline output into one machine-readable
object.

Design principles
─────────────────
- No LLM calls.
- No external API calls.
- Pure deterministic Python assembly from already-retrieved data.
- All field values come from objects created during the current run.
- Missing data is preserved as None, never invented.
- The object is fully JSON-serialisable via model_dump().
"""

import ast
from datetime import date
from typing import Optional, Any, Literal

from pydantic import BaseModel, Field

from agents.investment_strategist import InvestmentStrategy


# ============================================================
# MARKET SNAPSHOT
# ============================================================

class MarketSnapshot(BaseModel):
    """
    Verified market information retrieved by MarketDataTool
    from Yahoo Finance via yfinance at runtime.
    """

    source: str = Field(
        default="Yahoo Finance via yfinance",
        description="Data source for market snapshot."
    )

    current_price: Optional[float] = Field(
        default=None,
        description="Last traded price."
    )

    previous_close: Optional[float] = Field(
        default=None,
        description="Previous session closing price."
    )

    day_high: Optional[float] = Field(
        default=None,
        description="Intraday high."
    )

    day_low: Optional[float] = Field(
        default=None,
        description="Intraday low."
    )

    week_52_high: Optional[float] = Field(
        default=None,
        description="52-week high."
    )

    week_52_low: Optional[float] = Field(
        default=None,
        description="52-week low."
    )

    volume: Optional[float] = Field(
        default=None,
        description="Current session volume."
    )

    average_volume: Optional[float] = Field(
        default=None,
        description="Average daily volume."
    )

    market_cap: Optional[float] = Field(
        default=None,
        description="Market capitalisation in USD."
    )

    beta: Optional[float] = Field(
        default=None,
        description="Beta relative to the market."
    )

    dividend_yield: Optional[float] = Field(
        default=None,
        description="Trailing dividend yield."
    )


# ============================================================
# FINANCIAL SUMMARY  (SEC EDGAR)
# ============================================================

class FinancialSummary(BaseModel):
    """
    Official financial statement data retrieved from the
    SEC EDGAR XBRL Company Facts API.
    All monetary values are in USD.
    """

    source: str = Field(
        default="SEC EDGAR XBRL Company Facts API",
        description="Data source for financial summary."
    )

    # Reporting period metadata
    fiscal_year: Optional[int] = Field(
        default=None,
        description="Fiscal year of the reported period."
    )

    fiscal_period: Optional[str] = Field(
        default=None,
        description="Fiscal period (e.g. 'FY', 'Q3')."
    )

    period_start: Optional[str] = Field(
        default=None,
        description="Start date of the reporting period (ISO format)."
    )

    period_end: Optional[str] = Field(
        default=None,
        description="End date of the reporting period (ISO format)."
    )

    filed: Optional[str] = Field(
        default=None,
        description="SEC filing date (ISO format)."
    )

    # Income statement
    revenue: Optional[float] = Field(
        default=None,
        description="Total revenue in USD."
    )

    gross_profit: Optional[float] = Field(
        default=None,
        description="Gross profit in USD."
    )

    operating_income: Optional[float] = Field(
        default=None,
        description="Operating income in USD."
    )

    net_income: Optional[float] = Field(
        default=None,
        description="Net income in USD."
    )

    # Balance sheet
    assets: Optional[float] = Field(
        default=None,
        description="Total assets in USD."
    )

    liabilities: Optional[float] = Field(
        default=None,
        description="Total liabilities in USD."
    )

    stockholders_equity: Optional[float] = Field(
        default=None,
        description="Stockholders' equity in USD."
    )

    cash: Optional[float] = Field(
        default=None,
        description="Cash and cash equivalents in USD."
    )

    total_debt: Optional[float] = Field(
        default=None,
        description="Total debt (current + non-current) in USD."
    )

    # Cash flow statement
    operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Net cash from operating activities in USD."
    )

    capital_expenditure: Optional[float] = Field(
        default=None,
        description="Capital expenditure in USD (negative = outflow)."
    )


# ============================================================
# FINANCIAL METRICS  (Python Financial Metrics Engine)
# ============================================================

class FinancialMetrics(BaseModel):
    """
    Deterministic financial metrics calculated by the Python
    Financial Metrics Engine from normalised SEC data.
    All percentage values are expressed as percentages (e.g. 26.9
    means 26.9%). Ratio values are expressed as multiples (e.g. 1.16
    means 1.16x). Monetary values are in USD.
    Missing inputs produce None, never a fabricated value.
    """

    source: str = Field(
        default="Python Financial Metrics Engine",
        description="Calculation source."
    )

    revenue_growth: Optional[float] = Field(
        default=None,
        description="Year-over-year revenue growth (%)."
    )

    net_income_growth: Optional[float] = Field(
        default=None,
        description="Year-over-year net income growth (%)."
    )

    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross profit margin (%)."
    )

    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating income margin (%)."
    )

    net_profit_margin: Optional[float] = Field(
        default=None,
        description="Net profit margin (%)."
    )

    free_cash_flow: Optional[float] = Field(
        default=None,
        description="Free cash flow in USD (operating CF + CapEx)."
    )

    fcf_margin: Optional[float] = Field(
        default=None,
        description="Free cash flow margin (%)."
    )

    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Debt-to-equity ratio (%)."
    )

    net_cash: Optional[float] = Field(
        default=None,
        description="Net cash position in USD (cash minus total debt)."
    )

    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity (%)."
    )

    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets (%)."
    )

    asset_turnover: Optional[float] = Field(
        default=None,
        description="Asset turnover ratio (revenue / assets)."
    )

    equity_multiplier: Optional[float] = Field(
        default=None,
        description="Equity multiplier (assets / equity)."
    )


# ============================================================
# SPECIALIST REPORTS
# ============================================================

class SpecialistReports(BaseModel):
    """
    Plain-text outputs from the four specialist AI agents.
    Preserved as strings; not re-structured here.
    """

    financial_analyst: str = Field(
        description="Full text output from the Financial Research Analyst."
    )

    market_news_analyst: str = Field(
        description="Full text output from the Market & News Research Analyst."
    )

    valuation_analyst: str = Field(
        description="Full text output from the Valuation Research Analyst."
    )

    risk_analyst: str = Field(
        description="Full text output from the Risk Research Analyst."
    )


# ============================================================
# DATA SOURCES PROVENANCE
# ============================================================

class DataSources(BaseModel):
    """
    Provenance record identifying the origin of each data section
    in the final report.
    """

    market_data: str = Field(
        default="Yahoo Finance via yfinance",
        description="Source of market snapshot data."
    )

    financial_statements: str = Field(
        default="SEC EDGAR XBRL Company Facts API",
        description="Source of financial statement data."
    )

    news: str = Field(
        default="Marketaux",
        description="Source of news data."
    )

    metrics: str = Field(
        default="Python Financial Metrics Engine",
        description="Source of calculated financial metrics."
    )

    specialist_analysis: str = Field(
        default="AI Specialist Analysis (Google Gemini)",
        description="Source of specialist analyst reports."
    )

    investment_strategy: str = Field(
        default="AI Investment Strategist (Google Gemini)",
        description="Source of investment strategy and recommendation."
    )


# ============================================================
# HISTORICAL ANALYSIS & TRENDS
# ============================================================

class TrendSummary(BaseModel):
    revenue_trend: str = Field(default="Unavailable")
    net_income_trend: str = Field(default="Unavailable")
    debt_trend: str = Field(default="Unavailable")
    gross_margin_trend: str = Field(default="Unavailable")
    operating_margin_trend: str = Field(default="Unavailable")
    net_margin_trend: str = Field(default="Unavailable")
    revenue_cagr: Optional[float] = Field(default=None)
    net_income_cagr: Optional[float] = Field(default=None)

class HistoricalFinancialPoint(BaseModel):
    fy: int
    value: float
    unit: Optional[str] = Field(default=None)
    form: Optional[str] = Field(default=None)
    filed: Optional[str] = Field(default=None)
    start: Optional[str] = Field(default=None)
    end: Optional[str] = Field(default=None)

class HistoricalFinancials(BaseModel):
    revenue: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    gross_profit: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    operating_income: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    net_income: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    assets: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    liabilities: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    stockholders_equity: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    cash: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    total_debt: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    operating_cash_flow: Optional[list[HistoricalFinancialPoint]] = Field(default=None)
    capital_expenditure: Optional[list[HistoricalFinancialPoint]] = Field(default=None)

class HistoricalAnalysis(BaseModel):
    historical_financials: Optional[HistoricalFinancials] = Field(default=None)
    trend_summary: TrendSummary = Field(default_factory=TrendSummary)


# ============================================================
# EVIDENCE REGISTRY
# ============================================================

class EvidenceItem(BaseModel):
    """
    Structured item making research facts traceable to their source.
    """
    evidence_id: str = Field(description="Deterministic unique ID for this evidence item within the report.")
    evidence_type: Literal[
        "financial_fact",
        "market_data",
        "valuation_metric",
        "calculated_metric",
        "news",
        "reporting_metadata",
        "historical_financial"
    ] = Field(description="Categorical type of the evidence.")
    source: str = Field(description="Origin source of the data.")
    title: Optional[str] = Field(default=None, description="Optional title, e.g., for news articles.")
    claim: str = Field(description="What fact this item asserts.")
    value: Optional[Any] = Field(default=None, description="The numerical or textual value.")
    unit: Optional[str] = Field(default=None, description="Unit of measurement if applicable (e.g., USD, %).")
    period: Optional[str] = Field(default=None, description="Reporting period if applicable.")
    url: Optional[str] = Field(default=None, description="Source URL if applicable.")
    published_at: Optional[str] = Field(default=None, description="Publication timestamp if applicable.")
    metadata: dict = Field(default_factory=dict, description="Additional context or metadata.")


class EvidenceRegistry(BaseModel):
    """
    Deterministically constructed registry of factual claims 
    powering the investment research report.
    """
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="List of traceable evidence items."
    )


# ============================================================
# INVESTMENT RESEARCH REPORT  (canonical assembled object)
# ============================================================

class InvestmentResearchReport(BaseModel):
    """
    Canonical structured object representing the complete
    investment research report produced by the multi-agent pipeline.

    This object is the Phase 3.6 output. It is assembled
    deterministically in Python from data already retrieved and
    computed during the research run. No additional LLM or API calls
    are made to produce this object.

    The object is fully serialisable via model_dump() and
    json.dumps(report.model_dump()).
    """

    # ── Identity ──────────────────────────────────────────

    company: str = Field(
        description="Full company name."
    )

    ticker: str = Field(
        description="Stock ticker symbol."
    )

    research_date: str = Field(
        description=(
            "ISO format date (YYYY-MM-DD) on which the research was "
            "executed. Generated by Python datetime, not by the LLM."
        )
    )

    # ── Data sections ─────────────────────────────────────

    market_snapshot: MarketSnapshot = Field(
        description="Verified current market data from Yahoo Finance."
    )

    financial_summary: FinancialSummary = Field(
        description="Official financial statement data from SEC EDGAR."
    )

    financial_metrics: FinancialMetrics = Field(
        description="Deterministic metrics from the Python Financial Metrics Engine."
    )

    news: str = Field(
        description=(
            "Raw news research data from Marketaux as retrieved at "
            "runtime. Preserved as a string; not re-interpreted here."
        )
    )

    # ── AI outputs ────────────────────────────────────────

    specialist_reports: SpecialistReports = Field(
        description="Plain-text outputs from all four specialist AI agents."
    )

    investment_strategy: InvestmentStrategy = Field(
        description=(
            "Structured investment strategy produced by the Investment "
            "Strategist. Contains the final recommendation and confidence."
        )
    )

    # ── Provenance ────────────────────────────────────────

    data_sources: DataSources = Field(
        default_factory=DataSources,
        description="Record of data provenance for each report section."
    )
    
    evidence_registry: Optional[EvidenceRegistry] = Field(
        default=None,
        description="Structured registry making factual claims traceable."
    )
    
    historical_analysis: Optional[HistoricalAnalysis] = Field(
        default=None,
        description="Multi-year trend analysis based on historical financials."
    )
    
    trend_summary: Optional[TrendSummary] = Field(
        default=None,
        description="High-level trend labels for historical metrics."
    )


# ============================================================
# FACTORY FUNCTION
# ============================================================

def _safe_parse_market_string(market_data_str) -> dict:
    """
    Safely parse the string representation of the market data dict
    returned by MarketDataTool._run().

    MarketDataTool returns str(result_dict). This function converts
    it back to a Python dict using ast.literal_eval.
    Returns an empty dict on any parse failure.
    """

    if isinstance(market_data_str, dict):
        return market_data_str

    if not isinstance(market_data_str, str):
        return {}

    try:
        parsed = ast.literal_eval(market_data_str)
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, SyntaxError):
        pass

    return {}


def _extract_market_snapshot(market_data_str) -> MarketSnapshot:
    """
    Build a MarketSnapshot from the MarketDataTool output.
    All fields default to None on parse failure or missing keys.
    """

    raw = _safe_parse_market_string(market_data_str)
    md = raw.get("market_data", {})

    def _float(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    return MarketSnapshot(
        source=raw.get("source", "Yahoo Finance via yfinance"),
        current_price=_float(md.get("current_price")),
        previous_close=_float(md.get("previous_close")),
        day_high=_float(md.get("day_high")),
        day_low=_float(md.get("day_low")),
        week_52_high=_float(md.get("52_week_high")),
        week_52_low=_float(md.get("52_week_low")),
        volume=_float(md.get("volume")),
        average_volume=_float(md.get("average_volume")),
        market_cap=_float(md.get("market_cap")),
        beta=_float(md.get("beta")),
        dividend_yield=_float(md.get("dividend_yield")),
    )


def _extract_financial_summary(sec_data) -> FinancialSummary:
    """
    Build a FinancialSummary from the SECFinancialDataTool output dict.
    All fields default to None on missing keys.
    """

    if not isinstance(sec_data, dict):
        return FinancialSummary()

    metadata = sec_data.get("reporting_metadata", {})
    normalized = (
        sec_data
        .get("financial_data", {})
        .get("normalized", {})
    )

    def _int_or_none(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _float_or_none(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _str_or_none(value):
        if value is None:
            return None
        return str(value)

    return FinancialSummary(
        source="SEC EDGAR XBRL Company Facts API",
        fiscal_year=_int_or_none(metadata.get("fiscal_year")),
        fiscal_period=_str_or_none(metadata.get("fiscal_period")),
        period_start=_str_or_none(metadata.get("period_start")),
        period_end=_str_or_none(metadata.get("period_end")),
        filed=_str_or_none(metadata.get("filed")),
        revenue=_float_or_none(normalized.get("revenue")),
        gross_profit=_float_or_none(normalized.get("gross_profit")),
        operating_income=_float_or_none(normalized.get("operating_income")),
        net_income=_float_or_none(normalized.get("net_income")),
        assets=_float_or_none(normalized.get("assets")),
        liabilities=_float_or_none(normalized.get("liabilities")),
        stockholders_equity=_float_or_none(normalized.get("stockholders_equity")),
        cash=_float_or_none(normalized.get("cash")),
        total_debt=_float_or_none(normalized.get("total_debt")),
        operating_cash_flow=_float_or_none(normalized.get("operating_cash_flow")),
        capital_expenditure=_float_or_none(normalized.get("capital_expenditure")),
    )


def _extract_financial_metrics(metrics: dict) -> FinancialMetrics:
    """
    Build a FinancialMetrics from the metrics dict returned by
    FinancialMetricsEngine.calculate_from_sec_data().
    All fields default to None on missing or invalid values.
    """

    if not isinstance(metrics, dict):
        return FinancialMetrics()

    def _float_or_none(value):
        if value is None:
            return None
        try:
            f = float(value)
            # Guard against NaN or inf that would break JSON serialisation
            import math
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        except (TypeError, ValueError):
            return None

    return FinancialMetrics(
        source="Python Financial Metrics Engine",
        revenue_growth=_float_or_none(metrics.get("revenue_growth")),
        net_income_growth=_float_or_none(metrics.get("net_income_growth")),
        gross_margin=_float_or_none(metrics.get("gross_margin")),
        operating_margin=_float_or_none(metrics.get("operating_margin")),
        net_profit_margin=_float_or_none(metrics.get("net_profit_margin")),
        free_cash_flow=_float_or_none(metrics.get("free_cash_flow")),
        fcf_margin=_float_or_none(metrics.get("fcf_margin")),
        debt_to_equity=_float_or_none(metrics.get("debt_to_equity")),
        net_cash=_float_or_none(metrics.get("net_cash")),
        return_on_equity=_float_or_none(metrics.get("return_on_equity")),
        return_on_assets=_float_or_none(metrics.get("return_on_assets")),
        asset_turnover=_float_or_none(metrics.get("asset_turnover")),
        equity_multiplier=_float_or_none(metrics.get("equity_multiplier")),
    )


def build_investment_research_report(
    company: str,
    ticker: str,
    research_date: str,
    prepared: dict,
    specialist_results: dict,
    strategy: InvestmentStrategy,
    evidence_registry: Optional[EvidenceRegistry] = None,
    historical_analysis: Optional[HistoricalAnalysis] = None,
    trend_summary: Optional[TrendSummary] = None,
) -> "InvestmentResearchReport":
    """
    Assemble the final InvestmentResearchReport from pipeline outputs.

    Parameters
    ──────────
    company
        Full company name (e.g. "Apple Inc.").
    ticker
        Stock ticker symbol (e.g. "AAPL").
    research_date
        ISO format date string generated by Python datetime.date.today().
        Must NOT be provided by the LLM.
    prepared
        Dict returned by prepare_financial_research(). Expected keys:
            "market_data"    → str (MarketDataTool._run() output)
            "sec_data"       → dict (SECFinancialDataTool.get_financial_data())
            "financial_data" → str (FinancialDataTool._run() output)
            "news_data"      → str (NewsDataTool.run() output)
            "metrics"        → dict (FinancialMetricsEngine output)
    specialist_results
        Dict returned by run_specialists_in_parallel(). Keys are agent
        names; values are dicts with at minimum "report" (str).
    strategy
        InvestmentStrategy Pydantic object from strategy_result.pydantic.
        Must not be None.

    Returns
    ───────
    InvestmentResearchReport

    Raises
    ──────
    ValueError
        If strategy is None (structured output was not returned by the
        Investment Strategist).
    """

    if strategy is None:
        raise ValueError(
            "Cannot build InvestmentResearchReport: "
            "InvestmentStrategy is None. "
            "The Investment Strategist did not return structured output."
        )

    market_snapshot = _extract_market_snapshot(
        prepared.get("market_data", "")
    )

    financial_summary = _extract_financial_summary(
        prepared.get("sec_data", {})
    )

    financial_metrics = _extract_financial_metrics(
        prepared.get("metrics", {})
    )

    news_str = prepared.get("news_data", "")
    if not isinstance(news_str, str):
        news_str = str(news_str)

    specialist_reports = SpecialistReports(
        financial_analyst=specialist_results.get(
            "Financial Analyst", {}
        ).get("report", ""),
        market_news_analyst=specialist_results.get(
            "Market & News Analyst", {}
        ).get("report", ""),
        valuation_analyst=specialist_results.get(
            "Valuation Analyst", {}
        ).get("report", ""),
        risk_analyst=specialist_results.get(
            "Risk Analyst", {}
        ).get("report", ""),
    )

    return InvestmentResearchReport(
        company=company,
        ticker=ticker,
        research_date=research_date,
        market_snapshot=market_snapshot,
        financial_summary=financial_summary,
        financial_metrics=financial_metrics,
        news=news_str,
        specialist_reports=specialist_reports,
        investment_strategy=strategy,
        data_sources=DataSources(),
        evidence_registry=evidence_registry,
        historical_analysis=historical_analysis,
        trend_summary=trend_summary,
    )
