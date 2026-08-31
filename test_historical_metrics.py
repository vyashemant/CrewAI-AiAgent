import pytest
from tools.historical_metrics import HistoricalTrendEngine

def test_cagr_calculation():
    historical_data = {
        "revenue": [
            {"fy": 2021, "value": 100},
            {"fy": 2022, "value": 110},
            {"fy": 2023, "value": 121} # 10% CAGR over 2 years
        ]
    }
    
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    
    # 2023 - 2021 = 2 years elapsed.
    # 121 / 100 = 1.21. 1.21 ^ (1/2) = 1.1. So CAGR is 0.10 (10%)
    cagr = trends["metrics"]["revenue_cagr"]
    assert cagr is not None
    assert round(cagr, 2) == 0.10
    assert trends["labels"]["Revenue Trend"] == "Strong Growth"

def test_cagr_strong_growth():
    historical_data = {
        "net_income": [
            {"fy": 2022, "value": 100},
            {"fy": 2023, "value": 200} # 100% growth
        ]
    }
    
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    
    cagr = trends["metrics"]["net_income_cagr"]
    assert round(cagr, 2) == 1.00
    assert trends["labels"]["Net Income Trend"] == "Strong Growth"

def test_missing_data_cagr():
    historical_data = {
        "revenue": [
            {"fy": 2023, "value": 100} # Only one year
        ]
    }
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    
    assert trends["metrics"]["revenue_cagr"] is None
    assert trends["labels"]["Revenue Trend"] == "Unavailable"

def test_missing_year_gap():
    historical_data = {
        "revenue": [
            {"fy": 2021, "value": 100},
            {"fy": 2024, "value": 133.1} # 10% CAGR over 3 years
        ]
    }
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    
    cagr = trends["metrics"]["revenue_cagr"]
    assert cagr is not None
    assert round(cagr, 2) == 0.10
    
def test_negative_start_cagr():
    historical_data = {
        "net_income": [
            {"fy": 2021, "value": -100},
            {"fy": 2022, "value": 100}
        ]
    }
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    
    # Mathematical CAGR is invalid for negative starting values
    assert trends["metrics"]["net_income_cagr"] is None
    # However, since -100 -> 100 is an improvement, label should be Improving
    assert trends["labels"]["Net Income Trend"] == "Improving"

def test_debt_trend():
    historical_data = {
        "total_debt": [
            {"fy": 2021, "value": 1000},
            {"fy": 2022, "value": 900},
            {"fy": 2023, "value": 800} # Debt decreasing by more than 5%
        ]
    }
    
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    assert trends["labels"]["Debt Trend"] == "Improving"

    # Test increasing
    historical_data["total_debt"] = [
        {"fy": 2021, "value": 1000},
        {"fy": 2022, "value": 1100}
    ]
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    assert trends["labels"]["Debt Trend"] == "Increasing"

    # Test stable
    historical_data["total_debt"] = [
        {"fy": 2021, "value": 1000},
        {"fy": 2022, "value": 1020} # 2% increase is within 5% band
    ]
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    assert trends["labels"]["Debt Trend"] == "Stable"

def test_margin_trend():
    historical_data = {
        "revenue": [
            {"fy": 2022, "value": 1000},
            {"fy": 2023, "value": 2000}
        ],
        "gross_profit": [
            {"fy": 2022, "value": 300}, # 30% margin
            {"fy": 2023, "value": 800}  # 40% margin
        ]
    }
    
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    
    # Margin went from 30% to 40% (improving > 1% change)
    assert trends["labels"]["Gross Margin Trend"] == "Improving"

    # Test deteriorating
    historical_data["gross_profit"] = [
        {"fy": 2022, "value": 300}, # 30% margin
        {"fy": 2023, "value": 400}  # 20% margin
    ]
    engine = HistoricalTrendEngine(historical_data)
    trends = engine.get_trends()
    assert trends["labels"]["Gross Margin Trend"] == "Deteriorating"
