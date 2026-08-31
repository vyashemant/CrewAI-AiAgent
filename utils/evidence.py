import json
from typing import Optional

from agents.investment_research_report import EvidenceItem, EvidenceRegistry


def build_evidence_registry(canonical_evidence_json: str) -> EvidenceRegistry:
    """
    Deterministically build the Evidence Registry from the canonical JSON snapshot.
    """
    items = []
    
    try:
        canonical = json.loads(canonical_evidence_json)
    except (TypeError, ValueError):
        return EvidenceRegistry(evidence=[])

    metadata = canonical.get("metadata", {})
    market = canonical.get("market_data", {}).get("data", {})
    valuation = canonical.get("valuation_data", {}).get("data", {})
    sec = canonical.get("financial_data", {}).get("data", {})
    metrics = canonical.get("calculated_metrics", {}).get("data", {})
    news = canonical.get("news", {}).get("data", "")
    
    counters = {
        "SEC": 1,
        "MKT": 1,
        "VAL": 1,
        "CALC": 1,
        "NEWS": 1,
        "META": 1,
        "HIST": 1
    }
    
    def _get_id(prefix: str) -> str:
        val = counters[prefix]
        counters[prefix] += 1
        return f"{prefix}-{val:03d}"

    # 1. Reporting Metadata
    # While metadata is not explicitly detailed in canonical for SEC outside of 'metadata' section which just has ticker and date,
    # SEC reporting metadata might be passed in differently, but we'll extract ticker and research date here.
    if metadata.get("ticker"):
        items.append(
            EvidenceItem(
                evidence_id=_get_id("META"),
                evidence_type="reporting_metadata",
                source="System",
                claim="Research Ticker",
                value=metadata.get("ticker"),
                period=metadata.get("research_date")
            )
        )
    
    # Since we need to extract from SEC facts, let's look at the SEC fields.
    sec_fields = [
        ("revenue", "Revenue"),
        ("gross_profit", "Gross profit"),
        ("operating_income", "Operating income"),
        ("net_income", "Net income"),
        ("assets", "Assets"),
        ("liabilities", "Liabilities"),
        ("stockholders_equity", "Stockholders' equity"),
        ("cash", "Cash"),
        ("total_debt", "Total debt"),
        ("operating_cash_flow", "Operating cash flow"),
        ("capital_expenditure", "Capital expenditure")
    ]
    
    for key, claim_name in sec_fields:
        if isinstance(sec, dict) and sec.get(key) is not None:
            items.append(
                EvidenceItem(
                    evidence_id=_get_id("SEC"),
                    evidence_type="financial_fact",
                    source="SEC EDGAR XBRL Company Facts API",
                    claim=claim_name,
                    value=sec[key],
                    unit="USD"
                )
            )

    # 1.5 Historical Financial Evidence
    hist = canonical.get("financial_data", {}).get("historical", {})
    if isinstance(hist, dict):
        for key, claim_name in sec_fields:
            series = hist.get(key)
            if isinstance(series, list):
                for item in series:
                    fy = item.get("fy")
                    val = item.get("value")
                    if fy and val is not None:
                        items.append(
                            EvidenceItem(
                                evidence_id=_get_id("HIST"),
                                evidence_type="historical_financial",
                                source="SEC EDGAR XBRL Company Facts API",
                                claim=f"FY{fy} {claim_name}",
                                value=val,
                                unit="USD",
                                period=str(fy)
                            )
                        )

    # 2. Market Evidence
    market_fields = [
        ("current_price", "current price"),
        ("previous_close", "previous close"),
        ("52_week_high", "52-week high"),
        ("52_week_low", "52-week low"),
        ("volume", "volume"),
        ("market_cap", "market cap"),
        ("beta", "beta"),
        ("dividend_yield", "dividend yield")
    ]
    
    for key, claim_name in market_fields:
        if isinstance(market, dict) and market.get(key) is not None:
            unit = "USD" if key in ("current_price", "previous_close", "52_week_high", "52_week_low", "market_cap") else None
            items.append(
                EvidenceItem(
                    evidence_id=_get_id("MKT"),
                    evidence_type="market_data",
                    source="Yahoo Finance via yfinance",
                    claim=claim_name,
                    value=market[key],
                    unit=unit
                )
            )

    # 3. Valuation Evidence
    val_fields = [
        ("Trailing P/E", "trailing P/E"),
        ("Forward P/E", "forward P/E"),
        ("Price To Sales", "price-to-sales"),
        ("Price To Book", "price-to-book"),
        ("Enterprise Value", "enterprise value"),
        ("Enterprise To EBITDA", "EV/EBITDA")
    ]
    
    for key, claim_name in val_fields:
        if isinstance(valuation, dict) and valuation.get(key) is not None:
            unit = "USD" if key == "Enterprise Value" else None
            items.append(
                EvidenceItem(
                    evidence_id=_get_id("VAL"),
                    evidence_type="valuation_metric",
                    source="Yahoo Finance via yfinance",
                    claim=claim_name,
                    value=valuation[key],
                    unit=unit
                )
            )
            
    # 4. Calculated Metric Evidence
    calc_fields = [
        ("revenue_growth", "revenue growth", "%"),
        ("net_income_growth", "net income growth", "%"),
        ("gross_margin", "gross margin", "%"),
        ("operating_margin", "operating margin", "%"),
        ("net_profit_margin", "net profit margin", "%"),
        ("free_cash_flow", "free cash flow", "USD"),
        ("fcf_margin", "FCF margin", "%"),
        ("debt_to_equity", "debt-to-equity", "%"),
        ("net_cash", "net cash", "USD"),
        ("return_on_equity", "return on equity", "%"),
        ("return_on_assets", "return on assets", "%"),
        ("asset_turnover", "asset turnover", None),
        ("equity_multiplier", "equity multiplier", None)
    ]
    
    for key, claim_name, unit in calc_fields:
        if isinstance(metrics, dict) and metrics.get(key) is not None:
            items.append(
                EvidenceItem(
                    evidence_id=_get_id("CALC"),
                    evidence_type="calculated_metric",
                    source="Python Financial Metrics Engine",
                    claim=claim_name,
                    value=metrics[key],
                    unit=unit
                )
            )
            
    # 5. News Evidence
    # The news data is a dict containing 'articles'.
    if isinstance(news, dict):
        articles = news.get("articles", [])
        if isinstance(articles, list):
            for article in articles:
                if isinstance(article, dict):
                    items.append(
                        EvidenceItem(
                            evidence_id=_get_id("NEWS"),
                            evidence_type="news",
                            source="Marketaux",
                            claim="News article",
                            title=article.get("title"),
                            url=article.get("url"),
                            published_at=article.get("published_at"),
                            metadata={"source": article.get("source")} if article.get("source") else {}
                        )
                    )

    return EvidenceRegistry(evidence=items)
