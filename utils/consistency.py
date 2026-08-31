
import json
import ast
import re
from datetime import datetime

def safe_eval(val):
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return ast.literal_eval(val)
        except Exception:
            return val
    return val

def build_canonical_snapshot(ticker, prepared):
    """
    Build a JSON-serializable canonical research snapshot.
    """
    market_data_raw = safe_eval(prepared.get("market_data", {}))
    sec_data_raw = safe_eval(prepared.get("sec_data", {}))
    financial_data_raw = safe_eval(prepared.get("financial_data", {}))
    news_data_raw = safe_eval(prepared.get("news_data", {}))
    metrics = prepared.get("metrics", {})

    
    snapshot = {
        "metadata": {
            "ticker": ticker,
            "research_date": datetime.now().isoformat()
        },
        "market_data": {
            "type": "retrieved",
            "source": "Yahoo Finance",
            "data": market_data_raw.get("market_data", {}) if isinstance(market_data_raw, dict) else market_data_raw
        },
        "valuation_data": {
            "type": "retrieved",
            "source": "Yahoo Finance via yfinance",
            "data": financial_data_raw.get("valuation_metrics", {}) if isinstance(financial_data_raw, dict) else {}
        },
        "financial_data": {
            "type": "retrieved",
            "source": "SEC EDGAR",
            "data": sec_data_raw.get("financial_data", {}).get("normalized", {}) if isinstance(sec_data_raw, dict) else sec_data_raw,
            "historical": sec_data_raw.get("financial_data", {}).get("historical", {}) if isinstance(sec_data_raw, dict) else {}
        },
        "calculated_metrics": {
            "type": "calculated",
            "source": "Python Metrics Engine",
            "data": metrics
        },
        "news": {
            "type": "retrieved",
            "source": "Marketaux",
            "data": news_data_raw
        }
    }
    
    return json.dumps(snapshot, indent=2)

def validate_consistency(specialist_results, canonical_evidence):
    """
    Validate the specialist reports against the canonical evidence.
    Returns a status dict.
    """
    issues = []
    
    # Parse canonical evidence
    try:
        canonical = json.loads(canonical_evidence)
        metrics = canonical.get("calculated_metrics", {}).get("data", {})
        market = canonical.get("market_data", {}).get("data", {})
        valuation = canonical.get("valuation_data", {}).get("data", {})
    except Exception:
        metrics = {}
        market = {}
        valuation = {}

    # Basic deterministic checks
    # For example, if P/E is available in canonical but agent says unavailable
    # Or if market cap exists but agent says unavailable
    
    report_texts = []
    for result in specialist_results.values():
        if isinstance(result, dict) and "report" in result:
            report_texts.append(str(result["report"]))
        else:
            report_texts.append(str(result))

    combined_reports = " ".join(report_texts).lower()

    def mentions_unavailable(*patterns):
        return any(
            re.search(pattern, combined_reports)
            for pattern in patterns
        )
    
    if market.get("market_cap") is not None and mentions_unavailable(
        r"\bmarket\s+cap(?:italization)?\s+(?:is\s+)?unavailable\b",
        r"\bmarket\s+capitalisation\s+(?:is\s+)?unavailable\b"
    ):
        issues.append("An agent claimed market cap is unavailable, but it exists in canonical data.")
        
    if valuation.get("Trailing P/E") is not None and mentions_unavailable(
        r"\b(?:trailing\s+)?p/e\s+(?:is\s+)?unavailable\b",
        r"\b(?:trailing\s+)?pe\s+(?:is\s+)?unavailable\b",
        r"\bprice[-\s]?to[-\s]?earnings\s+(?:ratio\s+)?(?:is\s+)?unavailable\b"
    ):
        issues.append("An agent claimed P/E is unavailable, but it exists in canonical data.")
        
    if valuation.get("Price To Sales") is not None and mentions_unavailable(
        r"\bprice[-\s]?to[-\s]?sales\s+(?:ratio\s+)?(?:is\s+)?unavailable\b",
        r"\bp/s\s+(?:ratio\s+)?(?:is\s+)?unavailable\b"
    ):
        issues.append("An agent claimed Price to Sales is unavailable, but it exists in canonical data.")

    return {
        "status": "warning" if issues else "pass",
        "issues": issues
    }
