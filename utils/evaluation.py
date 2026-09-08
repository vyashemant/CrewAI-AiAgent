import json

def evaluate_research_quality(report: dict, canonical_evidence: str, consistency_status: dict) -> dict:
    """
    Deterministically evaluate the quality of a generated research report.
    Returns a dictionary of quality metrics.
    """
    scores = {
        "data_completeness": 0.0,
        "evidence_coverage": 0.0,
        "schema_validity": 1.0, # Assumes valid if it parsed into a dict
        "consistency_score": 1.0,
        "unavailable_data_rate": 0.0,
        "overall_score": 0.0
    }
    
    # Calculate Data Completeness & Unavailable Rate
    try:
        canonical = json.loads(canonical_evidence)
        financial_data = canonical.get("financial_data", {}).get("data", {})
        calculated_metrics = canonical.get("calculated_metrics", {}).get("data", {})
        
        all_metrics = list(financial_data.values()) + list(calculated_metrics.values())
        total_metrics = len(all_metrics)
        
        if total_metrics > 0:
            available_metrics = sum(1 for v in all_metrics if v is not None and v != "Unavailable")
            scores["data_completeness"] = round(available_metrics / total_metrics, 2)
            scores["unavailable_data_rate"] = round(1.0 - scores["data_completeness"], 2)
    except Exception:
        scores["data_completeness"] = 0.0
        scores["unavailable_data_rate"] = 1.0
        
    # Calculate Consistency Score
    if consistency_status.get("status") == "warning":
        issues_count = len(consistency_status.get("issues", []))
        # Reduce score by 0.1 for each issue, minimum 0
        scores["consistency_score"] = max(0.0, round(1.0 - (issues_count * 0.1), 2))
        
    # Calculate Evidence Coverage
    evidence_registry = report.get("evidence_registry", {})
    if evidence_registry:
        evidence_items = evidence_registry.get("evidence", [])
        if evidence_items:
            # We just check if there is some evidence for now. 
            # In a more complex system, this would map claims to evidence.
            scores["evidence_coverage"] = min(1.0, round(len(evidence_items) / 10.0, 2))
            
    # Calculate Overall Score (simple weighted average)
    scores["overall_score"] = round(
        (scores["data_completeness"] * 0.4) + 
        (scores["consistency_score"] * 0.4) + 
        (scores["evidence_coverage"] * 0.2), 
    2)
    
    return scores
