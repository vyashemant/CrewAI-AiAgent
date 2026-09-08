import pytest
from tools.financial_metrics import FinancialMetricsEngine

def test_financial_metrics_edge_cases():
    engine = FinancialMetricsEngine()
    
    # Division by zero
    assert engine.gross_margin(100, 0) is None
    assert engine.operating_margin(100, 0) is None
    assert engine.revenue_growth(100, 0) is None
    
    # Missing data
    assert engine.gross_margin(100, None) is None
    assert engine.gross_margin(None, 100) is None
    
    # Valid
    assert engine.gross_margin(50, 100) == 50.0
    
    # Full calc missing inputs
    res = engine.calculate_all(revenue=100, previous_revenue=None, gross_profit=None)
    assert res["revenue_growth"] is None
    assert res["gross_margin"] is None
