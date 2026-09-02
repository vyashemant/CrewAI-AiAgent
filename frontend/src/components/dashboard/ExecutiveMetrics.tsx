import type { FinancialSummary, FinancialMetrics } from '../../types/api';
import { formatPercentagePoints, formatLargeNumber } from '../../utils/formatters';

interface Props {
    summary: FinancialSummary;
    metrics: FinancialMetrics;
}

export function ExecutiveMetrics({ summary, metrics }: Props) {
    const getValue = (val: any, formatter: (v: any) => string) => {
        if (val === undefined || val === null) return 'Unavailable';
        return formatter(val);
    };

    return (
        <div className="kpi-grid" style={{ marginBottom: '1.5rem' }}>
            <div className="kpi-cell">
                <span className="kpi-label">Revenue</span>
                <span className="kpi-value">{getValue(summary.revenue, formatLargeNumber)}</span>
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">Net Income</span>
                <span className="kpi-value">{getValue(summary.net_income, formatLargeNumber)}</span>
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">Op Margin</span>
                <span className="kpi-value">{getValue(metrics.operating_margin, formatPercentagePoints)}</span>
                {metrics.operating_margin && metrics.operating_margin > 100 && (
                    <div style={{ fontSize: '0.625rem', color: 'var(--warning)', marginTop: '0.25rem', lineHeight: 1.2 }}>
                        DATA QUALITY WARNING:<br/>Mismatched reporting periods
                    </div>
                )}
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">FCF</span>
                <span className="kpi-value">{getValue(metrics.free_cash_flow, formatLargeNumber)}</span>
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">ROE</span>
                <span className="kpi-value">{getValue(metrics.return_on_equity, formatPercentagePoints)}</span>
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">Debt/Equity</span>
                <span className="kpi-value">{getValue(metrics.debt_to_equity, (v) => `${v.toFixed(2)}x`)}</span>
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">Assets</span>
                <span className="kpi-value">{getValue(summary.assets, formatLargeNumber)}</span>
            </div>
            <div className="kpi-cell">
                <span className="kpi-label">Cash</span>
                <span className="kpi-value">{getValue(summary.cash, formatLargeNumber)}</span>
            </div>
        </div>
    );
}
