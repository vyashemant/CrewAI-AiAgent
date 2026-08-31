import json
from utils.consistency import build_canonical_snapshot, validate_consistency

def test_validate_consistency_warning():
    # Canonical valuation data contains Trailing P/E
    canonical_data = {
        "calculated_metrics": {"data": {}},
        "market_data": {"data": {"market_cap": 2500000000000}},
        "valuation_data": {"data": {"Trailing P/E": 25.5, "Price To Sales": 10.2}}
    }
    
    # Specialist report says P/E is unavailable
    specialist_results = {
        "Financial Analyst": {
            "report": "The trailing P/E is unavailable for this company."
        }
    }
    
    result = validate_consistency(specialist_results, json.dumps(canonical_data))
    
    assert result["status"] == "warning"
    assert any("P/E is unavailable" in issue for issue in result["issues"])


def test_validate_consistency_pass():
    # Canonical valuation data contains P/E
    canonical_data = {
        "calculated_metrics": {"data": {}},
        "market_data": {"data": {"market_cap": 2500000000000}},
        "valuation_data": {"data": {"Trailing P/E": 25.5, "Price To Sales": 10.2}}
    }
    
    # Specialist report does not claim it is unavailable
    specialist_results = {
        "Financial Analyst": {
            "report": "The trailing P/E ratio is 25.5 and Price to Sales is 10.2."
        }
    }
    
    result = validate_consistency(specialist_results, json.dumps(canonical_data))
    
    assert result["status"] == "pass"
    assert len(result["issues"]) == 0

if __name__ == '__main__':
    test_validate_consistency_warning()
    test_validate_consistency_pass()
    print('All consistency tests passed!')
