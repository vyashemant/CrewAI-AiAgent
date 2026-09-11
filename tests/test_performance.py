import pytest
import time
from unittest.mock import patch

from services.research_pipeline import prepare_financial_research

@patch("services.research_pipeline.market_data_tool")
@patch("services.research_pipeline.sec_financial_tool")
@patch("services.research_pipeline.news_data_tool")
@patch("services.research_pipeline.financial_data_tool")
def test_data_retrieval_concurrency(mock_financial, mock_news, mock_sec, mock_market):
    """
    Test that the 3 data retrieval tools execute concurrently.
    If executed sequentially, the total time would be > 0.3 seconds.
    If executed concurrently, the total time should be ~0.1 seconds.
    """
    
    def slow_market(ticker):
        time.sleep(0.1)
        return {
            "market_data": "mock_market", 
            "valuation_metrics": {
                "Market Cap": 2500000000000.0,
                "Trailing P/E": 25.5,
                "Forward P/E": 22.0,
                "Price To Sales": 8.0,
                "Price To Book": 12.0,
                "Enterprise Value": 2400000000000.0,
                "Enterprise To EBITDA": 18.0
            }
        }

    def slow_sec(ticker):
        time.sleep(0.1)
        return {"sec_data": "mock_sec"}

    def slow_news(ticker, limit):
        time.sleep(0.1)
        return "mock_news"

    mock_market.fetch_data.side_effect = slow_market
    mock_sec.get_financial_data.side_effect = slow_sec
    mock_news.run.side_effect = slow_news

    start = time.perf_counter()
    prepared = prepare_financial_research("TEST")
    elapsed = time.perf_counter() - start

    # Assert time is less than sequential execution time (0.3s)
    # Give some generous overhead for thread creation (e.g. 0.25)
    assert elapsed < 0.25, f"Data retrieval took {elapsed}s, meaning it might not be fully concurrent."

    # Assert tools were called
    mock_market.fetch_data.assert_called_once_with("TEST")
    mock_sec.get_financial_data.assert_called_once_with("TEST")
    mock_news.run.assert_called_once_with(ticker="TEST", limit=3)

    # Assert the deprecated financial_data_tool was NOT called (to save API requests)
    mock_financial._run.assert_not_called()
    mock_financial.run.assert_not_called()

    # Verify MarketDataTool provides the valuation metrics
    expected_valuation = {
        "Market Cap": 2500000000000.0,
        "Trailing P/E": 25.5,
        "Forward P/E": 22.0,
        "Price To Sales": 8.0,
        "Price To Book": 12.0,
        "Enterprise Value": 2400000000000.0,
        "Enterprise To EBITDA": 18.0
    }
    
    # Assert that these exact values are present in prepared["financial_data"]["valuation_metrics"]
    assert prepared["financial_data"]["valuation_metrics"] == expected_valuation

    assert prepared["sec_data"] == {"sec_data": "mock_sec"}
    assert prepared["news_data"] == "mock_news"
