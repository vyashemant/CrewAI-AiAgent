import json
import pytest
from utils.evidence import build_evidence_registry
from agents.investment_research_report import EvidenceRegistry, EvidenceItem

@pytest.fixture
def mock_canonical_evidence():
    return json.dumps({
        "metadata": {
            "ticker": "AAPL",
            "research_date": "2026-08-31"
        },
        "market_data": {
            "type": "retrieved",
            "source": "Yahoo Finance",
            "data": {
                "current_price": 150.0,
                "volume": 1000000
            }
        },
        "valuation_data": {
            "type": "retrieved",
            "source": "Yahoo Finance via yfinance",
            "data": {
                "Trailing P/E": 25.5,
                "Enterprise Value": 2500000000000
            }
        },
        "financial_data": {
            "type": "retrieved",
            "source": "SEC EDGAR",
            "data": {
                "revenue": 350000000000,
                "net_income": None
            }
        },
        "calculated_metrics": {
            "type": "calculated",
            "source": "Python Metrics Engine",
            "data": {
                "revenue_growth": 10.5,
                "gross_margin": None
            }
        },
        "news": {
            "type": "retrieved",
            "source": "Marketaux",
            "data": {
                "articles": [
                    {
                        "title": "Apple releases new iPhone",
                        "url": "https://example.com/apple",
                        "published_at": "2026-08-30T10:00:00Z",
                        "source": "Tech News"
                    }
                ]
            }
        }
    })


def test_reporting_metadata_evidence(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    meta_evidence = [e for e in registry.evidence if e.evidence_type == "reporting_metadata"]
    assert len(meta_evidence) == 1
    assert meta_evidence[0].evidence_id == "META-001"
    assert meta_evidence[0].value == "AAPL"
    assert meta_evidence[0].period == "2026-08-31"


def test_sec_financial_evidence(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    sec_evidence = [e for e in registry.evidence if e.evidence_type == "financial_fact"]
    
    assert len(sec_evidence) == 1
    assert sec_evidence[0].evidence_id == "SEC-001"
    assert sec_evidence[0].claim == "Revenue"
    assert sec_evidence[0].value == 350000000000
    assert sec_evidence[0].unit == "USD"
    
    # Net income was None, should not be included
    claims = [e.claim for e in sec_evidence]
    assert "Net income" not in claims


def test_market_evidence(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    market_evidence = [e for e in registry.evidence if e.evidence_type == "market_data"]
    
    assert len(market_evidence) == 2
    claims = {e.claim: e.value for e in market_evidence}
    assert claims["current price"] == 150.0
    assert claims["volume"] == 1000000
    
    # Verify ID formatting
    assert market_evidence[0].evidence_id == "MKT-001"
    assert market_evidence[1].evidence_id == "MKT-002"


def test_valuation_evidence(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    val_evidence = [e for e in registry.evidence if e.evidence_type == "valuation_metric"]
    
    assert len(val_evidence) == 2
    claims = {e.claim: (e.value, e.unit) for e in val_evidence}
    
    assert claims["trailing P/E"] == (25.5, None)
    assert claims["enterprise value"] == (2500000000000, "USD")
    

def test_calculated_metric_evidence(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    calc_evidence = [e for e in registry.evidence if e.evidence_type == "calculated_metric"]
    
    assert len(calc_evidence) == 1
    assert calc_evidence[0].evidence_id == "CALC-001"
    assert calc_evidence[0].claim == "revenue growth"
    assert calc_evidence[0].value == 10.5
    assert calc_evidence[0].unit == "%"
    
    # gross_margin was None, should not be included
    claims = [e.claim for e in calc_evidence]
    assert "gross margin" not in claims


def test_news_evidence(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    news_evidence = [e for e in registry.evidence if e.evidence_type == "news"]
    
    assert len(news_evidence) == 1
    assert news_evidence[0].evidence_id == "NEWS-001"
    assert news_evidence[0].claim == "News article"
    assert news_evidence[0].title == "Apple releases new iPhone"
    assert news_evidence[0].url == "https://example.com/apple"
    assert news_evidence[0].published_at == "2026-08-30T10:00:00Z"
    assert news_evidence[0].metadata == {"source": "Tech News"}


def test_determinism_and_ordering(mock_canonical_evidence):
    registry1 = build_evidence_registry(mock_canonical_evidence)
    registry2 = build_evidence_registry(mock_canonical_evidence)
    
    assert len(registry1.evidence) == len(registry2.evidence)
    for idx, item1 in enumerate(registry1.evidence):
        item2 = registry2.evidence[idx]
        assert item1.evidence_id == item2.evidence_id
        assert item1.evidence_type == item2.evidence_type


def test_invalid_canonical_evidence():
    registry = build_evidence_registry("invalid json")
    assert len(registry.evidence) == 0


def test_registry_serialization(mock_canonical_evidence):
    registry = build_evidence_registry(mock_canonical_evidence)
    dumped = registry.model_dump_json()
    reconstructed = EvidenceRegistry.model_validate_json(dumped)
    
    assert len(reconstructed.evidence) == len(registry.evidence)
    assert reconstructed.evidence[0].evidence_id == registry.evidence[0].evidence_id
