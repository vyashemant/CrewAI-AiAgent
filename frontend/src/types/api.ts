export interface ResearchRequest {
    company: string;
    ticker: string;
}

export interface MarketSnapshot {
    current_price?: number | null;
    previous_close?: number | null;
    day_high?: number | null;
    day_low?: number | null;
    week_52_high?: number | null;
    week_52_low?: number | null;
    volume?: number | null;
    average_volume?: number | null;
    market_cap?: number | null;
    beta?: number | null;
    dividend_yield?: number | null;
    source?: string;
}

export interface FinancialSummary {
    revenue?: number | null;
    gross_profit?: number | null;
    operating_income?: number | null;
    net_income?: number | null;
    assets?: number | null;
    liabilities?: number | null;
    stockholders_equity?: number | null;
    cash?: number | null;
    total_debt?: number | null;
    operating_cash_flow?: number | null;
    capital_expenditure?: number | null;
    source?: string;
}

export interface FinancialMetrics {
    revenue_growth?: number | null;
    net_income_growth?: number | null;
    gross_margin?: number | null;
    operating_margin?: number | null;
    net_profit_margin?: number | null;
    free_cash_flow?: number | null;
    fcf_margin?: number | null;
    debt_to_equity?: number | null;
    net_cash?: number | null;
    return_on_equity?: number | null;
    return_on_assets?: number | null;
    asset_turnover?: number | null;
    equity_multiplier?: number | null;
    source?: string;
}

export interface TrendSummary {
    revenue_trend?: string;
    net_income_trend?: string;
    debt_trend?: string;
    gross_margin_trend?: string;
    operating_margin_trend?: string;
    net_margin_trend?: string;
    revenue_cagr?: number | null;
    net_income_cagr?: number | null;
}

export interface InvestmentStrategy {
    investment_thesis: string;
    fundamental_assessment: string;
    market_and_news_assessment: string;
    valuation_assessment: string;
    risk_assessment: string;
    bull_case: string;
    base_case: string;
    bear_case: string;
    key_catalysts: string[];
    key_risks: string[];
    thesis_change_triggers: string[];
    company_quality: string;
    valuation_view: string;
    recommendation: 'BUY' | 'HOLD' | 'SELL';
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
    evidence_summary: string;
    information_limitations: string;
    contradictions_detected?: string | null;
}

export interface SpecialistReports {
    financial_analyst: string;
    market_news_analyst: string;
    valuation_analyst: string;
    risk_analyst: string;
}

export interface DataSources {
    market_data: string;
    financial_statements: string;
    news: string;
    metrics: string;
    specialist_analysis: string;
    investment_strategy: string;
}

export interface EvidenceItem {
    evidence_id: string;
    evidence_type: string;
    source: string;
    title?: string | null;
    claim: string;
    value?: any;
    unit?: string | null;
    period?: string | null;
    url?: string | null;
    published_at?: string | null;
    metadata?: Record<string, any>;
}

export interface EvidenceRegistry {
    evidence: EvidenceItem[];
}

export interface InvestmentResearchReport {
    company: string;
    ticker: string;
    research_date: string;
    market_snapshot: MarketSnapshot;
    financial_summary: FinancialSummary;
    financial_metrics: FinancialMetrics;
    news: string;
    specialist_reports: SpecialistReports;
    investment_strategy: InvestmentStrategy;
    data_sources: DataSources;
    evidence_registry?: EvidenceRegistry | null;
    trend_summary?: TrendSummary | null;
}

export interface ResearchJobResponse {
    job_id: string;
    status: string;
    result?: InvestmentResearchReport | null;
    error?: string | null;
    created_at?: string | null;
    completed_at?: string | null;
}

export interface ResearchHistoryItem {
    job_id: string;
    company: string;
    ticker: string;
    status: string;
    created_at: string;
    completed_at?: string | null;
}

export interface ResearchHistoryResponse {
    research: ResearchHistoryItem[];
}
