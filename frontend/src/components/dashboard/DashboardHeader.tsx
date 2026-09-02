import type { InvestmentResearchReport } from '../../types/api';
import { formatDate, formatCurrency, formatLargeNumber, formatFractionAsPercentage } from '../../utils/formatters';

interface Props {
    report: InvestmentResearchReport;
}

export function DashboardHeader({ report }: Props) {
    const { 
        company, 
        ticker, 
        research_date,
        market_snapshot: { current_price, market_cap, previous_close },
        investment_strategy: { recommendation, confidence }
    } = report;

    let priceChange = null;
    let priceChangePercent = null;
    if (current_price != null && previous_close != null) {
        priceChange = current_price - previous_close;
        priceChangePercent = priceChange / previous_close;
    }
    
    const changeClass = priceChangePercent && priceChangePercent > 0 ? 'positive' : priceChangePercent && priceChangePercent < 0 ? 'negative' : 'neutral';
    
    const recClass = recommendation === 'BUY' ? 'badge-success' : recommendation === 'SELL' ? 'badge-danger' : 'badge-warning';
    const confClass = confidence === 'HIGH' ? 'text-success' : confidence === 'LOW' ? 'text-danger' : 'text-warning';

    return (
        <div className="terminal-header">
            <div className="header-main-info">
                <div className="company-title-row">
                    <h1 className="company-name">{company}</h1>
                    <span className="badge badge-neutral">{ticker}</span>
                    <span className={`badge ${recClass}`}>{recommendation}</span>
                </div>
                <div className="price-row">
                    <span className="current-price">{formatCurrency(current_price)}</span>
                    {priceChangePercent !== null && (
                        <span className={`price-change ${changeClass}`}>
                            {priceChangePercent > 0 ? '+' : ''}{formatFractionAsPercentage(priceChangePercent)}
                        </span>
                    )}
                </div>
            </div>
            
            <div className="header-meta">
                <div className="meta-row">
                    <span className="meta-label">Market Cap</span>
                    <span className="meta-value">{formatLargeNumber(market_cap)}</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">Research Date</span>
                    <span className="meta-value">{formatDate(research_date)}</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">Confidence</span>
                    <span className={`meta-value ${confClass}`}>
                        {confidence.charAt(0).toUpperCase() + confidence.slice(1).toLowerCase()}
                    </span>
                </div>
            </div>
        </div>
    );
}
