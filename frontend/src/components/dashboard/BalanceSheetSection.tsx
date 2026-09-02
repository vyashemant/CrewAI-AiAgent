
import type { FinancialSummary, FinancialMetrics  } from '../../types/api';
import { formatLargeNumber, formatPercentagePoints } from '../../utils/formatters';

interface Props {
    summary: FinancialSummary;
    metrics: FinancialMetrics;
}

export function BalanceSheetSection({ summary, metrics }: Props) {
    return (
        <div className="section-card">
            <h2 className="section-title">Balance Sheet & Leverage</h2>
            <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
                <div className="metric-box">
                    <span className="metric-value">{formatLargeNumber(summary.assets)}</span>
                    <span className="metric-label">Total Assets</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">{formatLargeNumber(summary.liabilities)}</span>
                    <span className="metric-label">Total Liabilities</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">{formatLargeNumber(summary.stockholders_equity)}</span>
                    <span className="metric-label">Stockholders' Equity</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">{formatLargeNumber(summary.cash)}</span>
                    <span className="metric-label">Cash & Equivalents</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">{formatLargeNumber(summary.total_debt)}</span>
                    <span className="metric-label">Total Debt</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">{formatPercentagePoints(metrics.debt_to_equity)}</span>
                    <span className="metric-label">Debt-to-Equity</span>
                </div>
                <div className="metric-box">
                    <span className="metric-value">
                        {metrics.net_cash !== undefined && metrics.net_cash !== null
                            ? formatLargeNumber(-metrics.net_cash) 
                            : 'Unavailable'}
                    </span>
                    <span className="metric-label">Net Debt</span>
                    <span className="sub-label">Based on cash & cash equivalents vs total debt.</span>
                </div>
            </div>
        </div>
    );
}
