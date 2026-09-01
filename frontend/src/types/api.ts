export interface ResearchRequest {
    company: string;
    ticker: string;
}

export interface MarketSnapshot {
    current_price?: number | null;
    market_cap?: number | null;
}

export interface FinancialSummary {
    revenue?: number | null;
    net_income?: number | null;
}

export interface TrendSummary {
    revenue_cagr?: number | null;
    net_income_cagr?: number | null;
}

export interface InvestmentStrategy {
    recommendation: 'BUY' | 'HOLD' | 'SELL';
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
    key_catalysts: string[];
    key_risks: string[];
}

export interface InvestmentResearchReport {
    company: string;
    ticker: string;
    research_date: string;
    market_snapshot: MarketSnapshot;
    financial_summary: FinancialSummary;
    investment_strategy: InvestmentStrategy;
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
