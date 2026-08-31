import json
from agents.investment_research_report import (
    build_investment_research_report,
    HistoricalAnalysis,
    HistoricalFinancials,
    HistoricalFinancialPoint,
    TrendSummary
)
from agents.investment_strategist import (
    InvestmentStrategy,
    ActionPlan,
    RiskAssessment
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
    market_data={},
    financial_data={},
    historical_analysis=historical_analysis,
    evidence_registry={"HIST-001": {"evidence_id": "HIST-001"}},
    financial_analysis="Financial analysis text",
    market_analysis="Market analysis text",
    valuation_analysis="Valuation text",
    risk_analysis="Risk text",
    strategy=InvestmentStrategy(
        recommendation="HOLD",
        confidence="HIGH",
        investment_horizon="1 Year",
        catalysts=[],
        evidence_summary="summary text",
        action_plan=ActionPlan(
            primary_action="Hold",
            entry_point=None,
            target_price=None,
            stop_loss=None,
            position_size=None,
            alternatives=None
        ),
        risk_assessment=RiskAssessment(
            risk_level="Medium",
            downside_risk="Downside",
            upside_potential="Upside",
            key_risks=[]
        )
    ),
    job_id="test-job"
)

# Serialize
print("Serialization test...")
json_str = final_report.model_dump_json()
print("Success!")
# Verify historical data made it in
data = json.loads(json_str)
assert data["historical_analysis"]["historical_financials"]["revenue"][0]["value"] == 100.0
print("Verification passed!")
