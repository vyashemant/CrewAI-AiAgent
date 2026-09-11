import pytest
import json
from unittest.mock import patch, MagicMock
from services.research_pipeline import run_investment_research

@pytest.fixture
def mock_market_data():
    return {
        "market_data": {
            "current_price": 150.0,
            "market_cap": 2500000000000.0,
            "beta": 1.2
        },
        "valuation_metrics": {
            "Trailing P/E": 25.5,
            "Enterprise Value": 2400000000000.0
        },
        "source": "Mock Market"
    }

@pytest.fixture
def mock_sec_data():
    return {
        "company": "Test Company",
        "reporting_metadata": {
            "fiscal_year": 2025,
            "fiscal_period": "FY"
        },
        "financial_data": {
            "normalized": {
                "revenue": 100000000.0,
                "gross_profit": 60000000.0,
                "operating_income": 30000000.0,
                "net_income": 25000000.0,
                "operating_cash_flow": 35000000.0,
                "capital_expenditure": -5000000.0,
                "cash": 50000000.0,
                "total_debt": 20000000.0,
                "assets": 150000000.0,
                "stockholders_equity": 100000000.0,
                "previous_revenue": 80000000.0,
                "previous_net_income": 20000000.0
            }
        }
    }

@patch("services.research_pipeline.market_data_tool")
@patch("services.research_pipeline.sec_financial_tool")
@patch("services.research_pipeline.financial_data_tool")
@patch("services.research_pipeline.news_data_tool")
@patch("services.research_pipeline.run_specialists_in_parallel")
@patch("services.research_pipeline.strategy_team")
def test_pipeline_healthy_company(mock_strategy, mock_specialists, mock_news, mock_fin, mock_sec, mock_mkt, mock_market_data, mock_sec_data):
    # Setup mocks
    mock_mkt.fetch_data.return_value = mock_market_data
    mock_sec.get_financial_data.return_value = mock_sec_data
    mock_news.run.return_value = "Mock News"
    
    # Mock specialist outputs
    mock_specialists.return_value = {
        "Financial Analyst": {"report": "Fin output", "elapsed": 1.0},
        "Market & News Analyst": {"report": "Market output", "elapsed": 1.0},
        "Valuation Analyst": {"report": "Val output", "elapsed": 1.0},
        "Risk Analyst": {"report": "Risk output", "elapsed": 1.0}
    }
    
    # Mock strategist output
    from agents.investment_strategist import InvestmentStrategy
    strategy_mock = MagicMock()
    strategy_mock.pydantic = InvestmentStrategy(
        recommendation="BUY",
        confidence="HIGH",
        investment_thesis="Good",
        company_quality="Mock quality",
        valuation_view="Mock valuation",
        fundamental_assessment="Mock fundamental",
        market_and_news_assessment="Mock market",
        valuation_assessment="Mock valuation assessment",
        risk_assessment="Mock risk",
        bull_case="Mock bull",
        base_case="Mock base",
        bear_case="Mock bear",
        key_catalysts=["Cat1"],
        key_risks=["Risk1"],
        thesis_change_triggers=["Trigger1"],
        evidence_summary="Mock evidence",
        information_limitations="Mock limits"
    )
    mock_strategy.kickoff.return_value = strategy_mock
    
    report, strategy, _, _, timing = run_investment_research("Test Company", "TST")
    
    assert report is not None
    assert report.company == "Test Company"
    assert report.ticker == "TST"
    assert report.financial_metrics.revenue_growth == 25.0
    assert report.financial_metrics.gross_margin == 60.0
    assert report.financial_metrics.net_cash == 30000000.0
    assert report.investment_strategy.recommendation == "BUY"

@patch("services.research_pipeline.market_data_tool")
@patch("services.research_pipeline.sec_financial_tool")
@patch("services.research_pipeline.financial_data_tool")
@patch("services.research_pipeline.news_data_tool")
@patch("services.research_pipeline.run_specialists_in_parallel")
@patch("services.research_pipeline.strategy_team")
def test_pipeline_missing_sec_data(mock_strategy, mock_specialists, mock_news, mock_fin, mock_sec, mock_mkt, mock_market_data):
    # Setup mocks
    mock_mkt.fetch_data.return_value = mock_market_data
    mock_sec.get_financial_data.return_value = {"error": "Not found"}
    mock_news.run.return_value = "Mock News"
    
    mock_specialists.return_value = {
        "Financial Analyst": {"report": "Fin output", "elapsed": 1.0},
        "Market & News Analyst": {"report": "Market output", "elapsed": 1.0},
        "Valuation Analyst": {"report": "Val output", "elapsed": 1.0},
        "Risk Analyst": {"report": "Risk output", "elapsed": 1.0}
    }
    
    from agents.investment_strategist import InvestmentStrategy
    strategy_mock = MagicMock()
    strategy_mock.pydantic = InvestmentStrategy(
        recommendation="HOLD",
        confidence="LOW",
        investment_thesis="No Data",
        company_quality="Mock quality",
        valuation_view="Mock valuation",
        fundamental_assessment="Mock fundamental",
        market_and_news_assessment="Mock market",
        valuation_assessment="Mock valuation assessment",
        risk_assessment="Mock risk",
        bull_case="Mock bull",
        base_case="Mock base",
        bear_case="Mock bear",
        key_catalysts=["Cat1"],
        key_risks=["Risk1"],
        thesis_change_triggers=["Trigger1"],
        evidence_summary="Mock evidence",
        information_limitations="Mock limits"
    )
    mock_strategy.kickoff.return_value = strategy_mock
    
    report, strategy, _, _, timing = run_investment_research("Test Company", "TST")
    
    assert report is not None
    assert report.financial_summary.revenue is None
    assert report.financial_metrics.gross_margin is None
