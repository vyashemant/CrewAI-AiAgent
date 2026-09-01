import json
from agents.investment_research_report import (
    build_investment_research_report,
    HistoricalAnalysis,
    HistoricalFinancials,
    HistoricalFinancialPoint,
    TrendSummary
)
from agents.investment_strategist import (
    InvestmentStrategy
)

# Mock data
historical_financials = HistoricalFinancials(
    revenue=[
        HistoricalFinancialPoint(fy=2022, value=100.0, unit="USD", form="10-K", filed="2023-01-01", start="2022-01-01", end="2022-12-31"),
        HistoricalFinancialPoint(fy=2023, value=110.0, unit="USD", form="10-K", filed="2024-01-01", start="2023-01-01", end="2023-12-31")
    ]
)

historical_analysis = HistoricalAnalysis(
    historical_financials=historical_financials,
    trend_summary=TrendSummary(revenue_trend="Moderate Growth", revenue_cagr=0.10)
)

final_report = build_investment_research_report(
    company="AAPL",
    ticker="AAPL",
    research_date="2026-09-01",
    prepared={"market_data": "", "sec_data": {}, "news_data": "", "metrics": {}},
    specialist_results={},
    strategy=InvestmentStrategy(
        investment_thesis="Thesis",
        fundamental_assessment="Fund",
        market_and_news_assessment="Market",
        valuation_assessment="Val",
        risk_assessment="Risk",
        bull_case="Bull",
        base_case="Base",
        bear_case="Bear",
        key_catalysts=[],
        key_risks=[],
        thesis_change_triggers=[],
        company_quality="Good",
        valuation_view="View",
        recommendation="HOLD",
        confidence="HIGH",
        evidence_summary="summary text",
        information_limitations="None",
        contradictions_detected="None"
    ),
    historical_analysis=historical_analysis,
    evidence_registry={"evidence": []}
)

# Serialize
print("Serialization test...")
json_str = final_report.model_dump_json()
print("Success!")
# Verify historical data made it in
data = json.loads(json_str)
assert data["historical_analysis"]["historical_financials"]["revenue"][0]["value"] == 100.0
print("Verification passed!")
