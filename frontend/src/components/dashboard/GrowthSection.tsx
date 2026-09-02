
import type { TrendSummary, FinancialMetrics  } from '../../types/api';
import { formatFractionAsPercentage } from '../../utils/formatters';

interface Props {
    trend: TrendSummary | null | undefined;
    metrics: FinancialMetrics;
}

export function GrowthSection({ trend, metrics }: Props) {
    return (
        <div className="section-card">
            <h2 className="section-title">Growth & Performance</h2>
            <div className="grid-4">
                <div className="metric-box">
                    <span className="metric-value">
                        {trend?.revenue_cagr !== undefined && trend?.revenue_cagr !== null 
                            ? formatFractionAsPercentage(trend.revenue_cagr) 
                            : <span style={{fontSize: '0.9rem', color: '#94a3b8'}}>Data unavailable</span>}
                    </span>
                    <span className="metric-label">Revenue CAGR</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">
                        {trend?.net_income_cagr !== undefined && trend?.net_income_cagr !== null 
                            ? formatFractionAsPercentage(trend.net_income_cagr) 
                            : <span style={{fontSize: '0.9rem', color: '#94a3b8'}}>Data unavailable</span>}
                    </span>
                    <span className="metric-label">Net Income CAGR</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">
                        {metrics.revenue_growth !== undefined && metrics.revenue_growth !== null 
                            ? formatFractionAsPercentage(metrics.revenue_growth) 
                            : <span style={{fontSize: '0.9rem', color: '#94a3b8'}}>Data unavailable</span>}
                    </span>
                    <span className="metric-label">YoY Revenue Growth</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">
                        {metrics.net_income_growth !== undefined && metrics.net_income_growth !== null 
                            ? formatFractionAsPercentage(metrics.net_income_growth) 
                            : <span style={{fontSize: '0.9rem', color: '#94a3b8'}}>Data unavailable</span>}
                    </span>
                    <span className="metric-label">YoY Net Income Growth</span>
                </div>
            </div>
        </div>
    );
}
