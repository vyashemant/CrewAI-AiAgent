"""
test_investment_research_report.py
────────────────────────────────────
Phase 3.6 unit tests for InvestmentResearchReport.

Uses fully representative / mock data.
No live API calls. No Gemini calls.

Tests:
 1.  company is preserved
 2.  ticker is preserved
 3.  research_date is present (non-empty string)
 4.  financial data is present
 5.  financial metrics are present
 6.  specialist reports are present
 7.  InvestmentStrategy is present (composed object)
 8.  recommendation is present
 9.  confidence is present
10.  model_dump() works
11.  JSON serialisation works
"""

import json
from datetime import date

from agents.investment_research_report import (
    InvestmentResearchReport,
    MarketSnapshot,
    FinancialSummary,
    FinancialMetrics,
    SpecialistReports,
    DataSources,
    build_investment_research_report,
)
from agents.investment_strategist import InvestmentStrategy


# ============================================================
# MOCK DATA
# ============================================================

# --- Mock prepared dict (as returned by prepare_financial_research) ---

# MarketDataTool._run() returns str(dict).  We replicate that here.
MOCK_MARKET_DATA_STR = str({
    "source": "Yahoo Finance via yfinance",
    "ticker": "AAPL",
    "company": "Apple Inc.",
    "market_data": {
        "current_price": 310.34,
        "previous_close": 309.35,
        "day_high": 312.00,
        "day_low": 308.50,
        "52_week_high": 344.57,
        "52_week_low": 224.69,
        "volume": 45000000.0,
        "average_volume": 55000000.0,
        "market_cap": 4530000000000.0,
        "beta": 1.086,
        "dividend_yield": 0.0035,
    },
    "recent_history": [],
})

# SECFinancialDataTool.get_financial_data() returns a dict directly.
MOCK_SEC_DATA = {
    "source": "SEC EDGAR XBRL Company Facts API",
    "ticker": "AAPL",
    "cik": "0000320193",
    "company": "Apple Inc.",
    "reporting_metadata": {
        "cik": "0000320193",
        "form": "10-K",
        "fiscal_year": 2025,
        "fiscal_period": "FY",
        "filed": "2025-11-01",
        "period_start": "2024-09-29",
        "period_end": "2025-09-27",
    },
    "financial_data": {
        "normalized": {
            "revenue": 416161000000.0,
            "gross_profit": 195201000000.0,
            "operating_income": 133050000000.0,
            "net_income": 112010000000.0,
            "assets": 359241000000.0,
            "liabilities": 285508000000.0,
            "stockholders_equity": 73733000000.0,
            "cash": 35934000000.0,
            "total_debt": 90678000000.0,
            "operating_cash_flow": 111482000000.0,
            "capital_expenditure": -12715000000.0,
        }
    },
}

# FinancialMetricsEngine.calculate_from_sec_data() returns a plain dict.
MOCK_METRICS = {
    "revenue_growth": 6.43,
    "net_income_growth": 19.49,
    "gross_margin": 46.91,
    "operating_margin": 31.97,
    "net_profit_margin": 26.92,
    "free_cash_flow": 98767000000.0,
    "fcf_margin": 23.73,
    "debt_to_equity": 144.58,
    "net_cash": -54744000000.0,
    "return_on_equity": 151.91,
    "return_on_assets": 31.18,
    "asset_turnover": 1.16,
    "equity_multiplier": 4.87,
}

MOCK_PREPARED = {
    "market_data": MOCK_MARKET_DATA_STR,
    "sec_data": MOCK_SEC_DATA,
    "financial_data": "{}",       # not used in final report assembly
    "news_data": (
        "Recent news: Apple is preparing a new Mac mini launch. "
        "Source: Marketaux, 2026-08-25."
    ),
    "metrics": MOCK_METRICS,
}

# --- Mock specialist results (as returned by run_specialists_in_parallel) ---

MOCK_SPECIALIST_RESULTS = {
    "Financial Analyst": {
        "name": "Financial Analyst",
        "report": (
            "FINANCIAL RESEARCH REPORT - Apple Inc. (AAPL)\n"
            "Revenue: $416.161B, Gross Margin: 46.91%\n"
            "Overall: Strong financial health."
        ),
        "elapsed": 12.5,
    },
    "Market & News Analyst": {
        "name": "Market & News Analyst",
        "report": (
            "MARKET AND NEWS REPORT - Apple Inc. (AAPL)\n"
            "Mac mini refresh reported. Beta: 1.086."
        ),
        "elapsed": 10.2,
    },
    "Valuation Analyst": {
        "name": "Valuation Analyst",
        "report": (
            "VALUATION REPORT - Apple Inc. (AAPL)\n"
            "Trailing P/E: 35.47x. EV/EBITDA: 27.10x. Premium valuation."
        ),
        "elapsed": 11.0,
    },
    "Risk Analyst": {
        "name": "Risk Analyst",
        "report": (
            "RISK ANALYSIS REPORT - Apple Inc. (AAPL)\n"
            "Valuation risk HIGH. Financial risk MODERATE."
        ),
        "elapsed": 9.8,
    },
}

# --- Mock InvestmentStrategy ---

MOCK_STRATEGY = InvestmentStrategy(
    investment_thesis=(
        "Apple Inc. is a high-quality business with exceptional "
        "profitability and cash generation. However, premium valuation "
        "multiples leave limited margin of safety at current prices."
    ),
    fundamental_assessment=(
        "Strong fundamentals: revenue growth 6.43%, gross margin 46.91%, "
        "free cash flow $98.767B."
    ),
    market_and_news_assessment=(
        "Limited news. Mac mini refresh reported but unconfirmed. "
        "Beta 1.086."
    ),
    valuation_assessment=(
        "Expensive across all metrics. Trailing P/E 35.47x, EV/EBITDA 27.10x. "
        "No margin of safety visible."
    ),
    risk_assessment=(
        "Primary risk is valuation. Business quality is high but the stock "
        "leaves little room for fundamental underperformance."
    ),
    bull_case=(
        "Services acceleration and AI integration drive revenue growth "
        "well above 6%, supporting current multiples."
    ),
    base_case=(
        "Apple maintains current margins and moderate growth. Stock "
        "delivers returns broadly in line with earnings growth."
    ),
    bear_case=(
        "Revenue growth disappoints, triggering multiple compression "
        "from elevated starting levels."
    ),
    key_catalysts=[
        "Services revenue acceleration",
        "Mac mini product refresh",
        "AI-related ecosystem growth",
    ],
    key_risks=[
        "Multiple compression risk at elevated valuations",
        "Revenue growth deceleration",
        "Macro consumer spending deterioration",
    ],
    thesis_change_triggers=[
        "Revenue growth falls below 3% for two consecutive quarters",
        "Gross margin contracts materially",
        "Free cash flow declines year-over-year",
    ],
    company_quality=(
        "Exceptional. Apple has best-in-class profitability, strong FCF, "
        "and a durable ecosystem competitive position."
    ),
    valuation_view=(
        "Expensive. Current multiples imply continued high growth and "
        "margin durability. No visible margin of safety."
    ),
    recommendation="HOLD",
    confidence="MEDIUM",
    evidence_summary=(
        "Verified facts: revenue $416B, FCF $98.8B, gross margin 46.91%. "
        "Valuation: trailing P/E 35.47x, EV/EBITDA 27.10x."
    ),
    information_limitations=(
        "No peer data. No forward estimates. No historical valuation range. "
        "News coverage limited to two articles."
    ),
    contradictions_detected=None,
)

MOCK_RESEARCH_DATE = date.today().isoformat()


# ============================================================
# HELPER – build report once for all tests
# ============================================================

def make_report() -> InvestmentResearchReport:
    """Build and return the report using mock data."""
    return build_investment_research_report(
        company="Apple Inc.",
        ticker="AAPL",
        research_date=MOCK_RESEARCH_DATE,
        prepared=MOCK_PREPARED,
        specialist_results=MOCK_SPECIALIST_RESULTS,
        strategy=MOCK_STRATEGY,
    )


# ============================================================
# TESTS
# ============================================================

def test_01_company_preserved():
    """Test 1: company is preserved."""
    report = make_report()
    assert report.company == "Apple Inc.", (
        f"Expected 'Apple Inc.' but got '{report.company}'"
    )
    print("PASS  test_01_company_preserved")


def test_02_ticker_preserved():
    """Test 2: ticker is preserved."""
    report = make_report()
    assert report.ticker == "AAPL", (
        f"Expected 'AAPL' but got '{report.ticker}'"
    )
    print("PASS  test_02_ticker_preserved")


def test_03_research_date_present():
    """Test 3: research_date is a non-empty ISO date string."""
    report = make_report()
    assert isinstance(report.research_date, str), (
        f"research_date must be a str, got {type(report.research_date)}"
    )
    assert len(report.research_date) == 10, (
        f"Expected ISO date length 10, got '{report.research_date}'"
    )
    # Must be parseable as a date
    parsed = date.fromisoformat(report.research_date)
    assert parsed is not None
    print("PASS  test_03_research_date_present")


def test_04_financial_data_present():
    """Test 4: financial_summary contains real data."""
    report = make_report()
    fs = report.financial_summary

    assert fs.revenue is not None, "revenue should not be None"
    assert fs.revenue > 0, f"revenue should be positive, got {fs.revenue}"
    assert fs.net_income is not None, "net_income should not be None"
    assert fs.fiscal_year == 2025, (
        f"Expected fiscal_year=2025, got {fs.fiscal_year}"
    )
    print("PASS  test_04_financial_data_present")


def test_05_financial_metrics_present():
    """Test 5: financial_metrics contains real calculated values."""
    report = make_report()
    fm = report.financial_metrics

    assert fm.gross_margin is not None, "gross_margin should not be None"
    assert fm.gross_margin > 0, (
        f"gross_margin should be positive, got {fm.gross_margin}"
    )
    assert fm.free_cash_flow is not None, "free_cash_flow should not be None"
    assert fm.revenue_growth is not None, "revenue_growth should not be None"
    print("PASS  test_05_financial_metrics_present")


def test_06_specialist_reports_present():
    """Test 6: all four specialist reports are present and non-empty."""
    report = make_report()
    sr = report.specialist_reports

    assert isinstance(sr.financial_analyst, str) and sr.financial_analyst, (
        "financial_analyst report should be a non-empty string"
    )
    assert isinstance(sr.market_news_analyst, str) and sr.market_news_analyst, (
        "market_news_analyst report should be a non-empty string"
    )
    assert isinstance(sr.valuation_analyst, str) and sr.valuation_analyst, (
        "valuation_analyst report should be a non-empty string"
    )
    assert isinstance(sr.risk_analyst, str) and sr.risk_analyst, (
        "risk_analyst report should be a non-empty string"
    )
    print("PASS  test_06_specialist_reports_present")


def test_07_investment_strategy_present():
    """Test 7: investment_strategy is the composed InvestmentStrategy object."""
    report = make_report()
    assert isinstance(report.investment_strategy, InvestmentStrategy), (
        f"investment_strategy must be InvestmentStrategy, "
        f"got {type(report.investment_strategy)}"
    )
    print("PASS  test_07_investment_strategy_present")


def test_08_recommendation_present():
    """Test 8: recommendation is a valid string (BUY / HOLD / SELL)."""
    report = make_report()
    rec = report.investment_strategy.recommendation
    assert rec in ("BUY", "HOLD", "SELL"), (
        f"recommendation must be BUY/HOLD/SELL, got '{rec}'"
    )
    print("PASS  test_08_recommendation_present")


def test_09_confidence_present():
    """Test 9: confidence is a valid string (LOW / MEDIUM / HIGH)."""
    report = make_report()
    conf = report.investment_strategy.confidence
    assert conf in ("LOW", "MEDIUM", "HIGH"), (
        f"confidence must be LOW/MEDIUM/HIGH, got '{conf}'"
    )
    print("PASS  test_09_confidence_present")


def test_10_model_dump_works():
    """Test 10: model_dump() produces a valid non-empty dict."""
    report = make_report()
    dumped = report.model_dump()

    assert isinstance(dumped, dict), (
        f"model_dump() should return dict, got {type(dumped)}"
    )
    assert "company" in dumped
    assert "ticker" in dumped
    assert "research_date" in dumped
    assert "market_snapshot" in dumped
    assert "financial_summary" in dumped
    assert "financial_metrics" in dumped
    assert "specialist_reports" in dumped
    assert "investment_strategy" in dumped
    assert "data_sources" in dumped

    # Nested strategy should be present
    assert "recommendation" in dumped["investment_strategy"]
    assert "confidence" in dumped["investment_strategy"]

    print("PASS  test_10_model_dump_works")


def test_11_json_serialisation_works():
    """Test 11: JSON serialisation produces a valid non-empty JSON string."""
    report = make_report()
    dumped = report.model_dump()

    json_str = json.dumps(dumped, default=str)

    assert isinstance(json_str, str) and json_str, (
        "json.dumps() should return a non-empty string"
    )

    # Round-trip: deserialise and verify key fields
    reparsed = json.loads(json_str)
    assert reparsed["company"] == "Apple Inc."
    assert reparsed["ticker"] == "AAPL"
    assert reparsed["investment_strategy"]["recommendation"] == "HOLD"

    print("PASS  test_11_json_serialisation_works")


# ============================================================
# ADDITIONAL EDGE-CASE TESTS
# ============================================================

def test_12_missing_market_data_graceful():
    """Edge case: empty market_data string should not crash."""
    prepared = dict(MOCK_PREPARED)
    prepared["market_data"] = ""

    report = build_investment_research_report(
        company="Apple Inc.",
        ticker="AAPL",
        research_date=MOCK_RESEARCH_DATE,
        prepared=prepared,
        specialist_results=MOCK_SPECIALIST_RESULTS,
        strategy=MOCK_STRATEGY,
    )

    # All market fields should be None, not an error
    assert report.market_snapshot.current_price is None
    assert report.market_snapshot.market_cap is None
    print("PASS  test_12_missing_market_data_graceful")


def test_13_none_strategy_raises():
    """Edge case: None strategy must raise ValueError."""
    raised = False
    try:
        build_investment_research_report(
            company="Apple Inc.",
            ticker="AAPL",
            research_date=MOCK_RESEARCH_DATE,
            prepared=MOCK_PREPARED,
            specialist_results=MOCK_SPECIALIST_RESULTS,
            strategy=None,
        )
    except ValueError:
        raised = True

    assert raised, "build_investment_research_report should raise ValueError when strategy is None"
    print("PASS  test_13_none_strategy_raises")


def test_14_none_metrics_graceful():
    """Edge case: None metrics in prepared should result in all-None FinancialMetrics."""
    prepared = dict(MOCK_PREPARED)
    prepared["metrics"] = {
        "revenue_growth": None,
        "net_income_growth": None,
        "gross_margin": None,
        "operating_margin": None,
        "net_profit_margin": None,
        "free_cash_flow": None,
        "fcf_margin": None,
        "debt_to_equity": None,
        "net_cash": None,
        "return_on_equity": None,
        "return_on_assets": None,
        "asset_turnover": None,
        "equity_multiplier": None,
    }

    report = build_investment_research_report(
        company="Apple Inc.",
        ticker="AAPL",
        research_date=MOCK_RESEARCH_DATE,
        prepared=prepared,
        specialist_results=MOCK_SPECIALIST_RESULTS,
        strategy=MOCK_STRATEGY,
    )

    assert report.financial_metrics.revenue_growth is None
    assert report.financial_metrics.gross_margin is None
    print("PASS  test_14_none_metrics_graceful")


# ============================================================
# RUN ALL TESTS
# ============================================================

if __name__ == "__main__":

    tests = [
        test_01_company_preserved,
        test_02_ticker_preserved,
        test_03_research_date_present,
        test_04_financial_data_present,
        test_05_financial_metrics_present,
        test_06_specialist_reports_present,
        test_07_investment_strategy_present,
        test_08_recommendation_present,
        test_09_confidence_present,
        test_10_model_dump_works,
        test_11_json_serialisation_works,
        test_12_missing_market_data_graceful,
        test_13_none_strategy_raises,
        test_14_none_metrics_graceful,
    ]

    print("\n")
    print("=" * 60)
    print("INVESTMENT RESEARCH REPORT — UNIT TESTS")
    print("=" * 60)

    passed = 0
    failed = 0
    errors = []

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as exc:
            failed += 1
            errors.append((test_fn.__name__, str(exc)))
            print(f"FAIL  {test_fn.__name__}: {exc}")

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")

    if errors:
        print("\nFailed tests:")
        for name, msg in errors:
            print(f"  - {name}: {msg}")
        raise SystemExit(1)

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
