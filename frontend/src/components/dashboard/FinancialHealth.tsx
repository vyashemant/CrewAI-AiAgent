import { FileSpreadsheet } from 'lucide-react';
import type { FinancialSummary, FinancialMetrics } from '../../types/api';
import { formatLargeNumber, formatPercentagePoints, formatRatio } from '../../utils/formatters';

interface Props {
    summary: FinancialSummary;
    metrics: FinancialMetrics;
}

export function FinancialHealth({ summary, metrics }: Props) {
    const getValue = (val: any, formatter: (v: any) => string) => {
        if (val === undefined || val === null) return 'Unavailable';
        return formatter(val);
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <div className="panel-title">
                    <FileSpreadsheet size={16} />
                    Financial Statements & Health
                </div>
            </div>

            <div className="grid-2">
                <div>
                    <div className="panel-title" style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Reported Financials</div>
                    <table className="terminal-table">
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th className="right-align">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Revenue</td>
                                <td className="numeric">{getValue(summary.revenue, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Gross Profit</td>
                                <td className="numeric">{getValue(summary.gross_profit, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Operating Income</td>
                                <td className="numeric">{getValue(summary.operating_income, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Net Income</td>
                                <td className="numeric">{getValue(summary.net_income, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Operating Cash Flow</td>
                                <td className="numeric">{getValue(summary.operating_cash_flow, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Capital Expenditure</td>
                                <td className="numeric">{getValue(summary.capital_expenditure, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Free Cash Flow</td>
                                <td className="numeric">{getValue(metrics.free_cash_flow, formatLargeNumber)}</td>
                            </tr>
                            <tr>
                                <td>Total Assets</td>
                                <td className="numeric">{getValue(summary.assets, formatLargeNumber)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div>
                    <div className="panel-title" style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Calculated Metrics</div>
                    <table className="terminal-table">
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th className="right-align">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Gross Margin</td>
                                <td className="numeric">
                                    {getValue(metrics.gross_margin, formatPercentagePoints)}
                                    {metrics.gross_margin && metrics.gross_margin > 100 && (
                                        <div style={{ fontSize: '0.625rem', color: 'var(--warning)', marginTop: '0.25rem', lineHeight: 1.2 }}>
                                            DATA QUALITY WARNING:<br/>Mismatched reporting periods
                                        </div>
                                    )}
                                </td>
                            </tr>
                            <tr>
                                <td>Operating Margin</td>
                                <td className="numeric">
                                    {getValue(metrics.operating_margin, formatPercentagePoints)}
                                    {metrics.operating_margin && metrics.operating_margin > 100 && (
                                        <div style={{ fontSize: '0.625rem', color: 'var(--warning)', marginTop: '0.25rem', lineHeight: 1.2 }}>
                                            DATA QUALITY WARNING:<br/>Mismatched reporting periods
                                        </div>
                                    )}
                                </td>
                            </tr>
                            <tr>
                                <td>Net Profit Margin</td>
                                <td className="numeric">
                                    {getValue(metrics.net_profit_margin, formatPercentagePoints)}
                                    {metrics.net_profit_margin && metrics.net_profit_margin > 100 && (
                                        <div style={{ fontSize: '0.625rem', color: 'var(--warning)', marginTop: '0.25rem', lineHeight: 1.2 }}>
                                            DATA QUALITY WARNING:<br/>Mismatched reporting periods
                                        </div>
                                    )}
                                </td>
                            </tr>
                            <tr>
                                <td>FCF Margin</td>
                                <td className="numeric">{getValue(metrics.fcf_margin, formatPercentagePoints)}</td>
                            </tr>
                            <tr>
                                <td>Return on Assets</td>
                                <td className="numeric">{getValue(metrics.return_on_assets, formatPercentagePoints)}</td>
                            </tr>
                            <tr>
                                <td>Return on Equity</td>
                                <td className="numeric">{getValue(metrics.return_on_equity, formatPercentagePoints)}</td>
                            </tr>
                            <tr>
                                <td>Asset Turnover</td>
                                <td className="numeric">{getValue(metrics.asset_turnover, formatRatio)}</td>
                            </tr>
                            <tr>
                                <td>Equity Multiplier</td>
                                <td className="numeric">{getValue(metrics.equity_multiplier, formatRatio)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
