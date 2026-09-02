import { DatabaseZap } from 'lucide-react';
import type { EvidenceRegistry } from '../../types/api';
import { formatCurrency, formatPercentagePoints, formatRatio } from '../../utils/formatters';

interface Props {
    registry: EvidenceRegistry | null | undefined;
}

export function EvidencePanel({ registry }: Props) {
    if (!registry || !registry.evidence || registry.evidence.length === 0) return null;

    const renderValue = (val: any, unit?: string | null) => {
        if (val === null || val === undefined) return 'N/A';
        if (typeof val === 'number') {
            if (unit === 'USD') return formatCurrency(val);
            if (unit === '%') return formatPercentagePoints(val);
            if (unit === 'x') return formatRatio(val);
            return val.toFixed(2);
        }
        return String(val);
    };

    return (
        <div className="panel">
            <div className="panel-header">
                <div className="panel-title">
                    <DatabaseZap size={16} />
                    Data Provenance & Evidence
                </div>
            </div>
            
            <div className="evidence-table-container">
                <table className="terminal-table evidence-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Type</th>
                            <th>Source</th>
                            <th>Claim</th>
                            <th className="right-align">Value</th>
                            <th>Period</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {registry.evidence.map((item, idx) => {
                            const isCalc = item.evidence_type === 'calculated_metric';
                            const status = isCalc ? 'Calculated' : item.evidence_type === 'news' ? 'Retrieved' : 'Verified';
                            const statusClass = isCalc ? 'badge-warning' : item.evidence_type === 'news' ? 'badge-neutral' : 'badge-success';

                            return (
                                <tr key={idx}>
                                    <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontFamily: 'var(--mono)' }}>{item.evidence_id}</td>
                                    <td style={{ fontSize: '0.75rem' }}>{item.evidence_type}</td>
                                    <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{item.source}</td>
                                    <td style={{ fontWeight: 500 }}>{item.claim}</td>
                                    <td className="numeric">{renderValue(item.value, item.unit)}</td>
                                    <td style={{ fontSize: '0.75rem' }}>{item.period || '-'}</td>
                                    <td><span className={`badge ${statusClass}`} style={{ fontSize: '0.625rem' }}>{status}</span></td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
