import { Calculator } from 'lucide-react';
import type { EvidenceRegistry } from '../../types/api';
import { formatRatio } from '../../utils/formatters';

interface Props {
    registry: EvidenceRegistry | null | undefined;
}

export function ValuationSection({ registry }: Props) {
    if (!registry || !registry.evidence) {
        return (
            <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="panel-header">
                    <div className="panel-title"><Calculator size={16} /> Valuation</div>
                </div>
                <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                    Data Unavailable
                </div>
            </div>
        );
    }

    const valMetrics = registry.evidence.filter(e => e.evidence_type === 'valuation_metric');
    
    const trailingPE = valMetrics.find(e => e.claim.toLowerCase().includes('trailing p/e'))?.value;
    const forwardPE = valMetrics.find(e => e.claim.toLowerCase().includes('forward p/e'))?.value;
    const ps = valMetrics.find(e => e.claim.toLowerCase().includes('price-to-sales'))?.value;
    const pb = valMetrics.find(e => e.claim.toLowerCase().includes('price-to-book'))?.value;
    const evEbitda = valMetrics.find(e => e.claim.toLowerCase().includes('ev/ebitda'))?.value;

    const getValue = (val: any) => val ? formatRatio(val) : 'Unavailable';
    
    const getInterpretation = (val: any) => {
        if (!val) return '-';
        if (typeof val === 'string') val = parseFloat(val);
        if (isNaN(val)) return '-';
        if (val > 30) return 'Premium';
        if (val > 15) return 'Fair';
        return 'Discounted';
    };

    return (
        <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div className="panel-header">
                <div className="panel-title"><Calculator size={16} /> Valuation</div>
            </div>
            
            <table className="terminal-table" style={{ width: '100%' }}>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th className="right-align">Value</th>
                        <th>Interpretation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Trailing P/E</td>
                        <td className="numeric">{getValue(trailingPE)}</td>
                        <td><span className="badge badge-neutral">{getInterpretation(trailingPE)}</span></td>
                    </tr>
                    <tr>
                        <td>Forward P/E</td>
                        <td className="numeric">{getValue(forwardPE)}</td>
                        <td><span className="badge badge-neutral">{getInterpretation(forwardPE)}</span></td>
                    </tr>
                    <tr>
                        <td>Price/Sales</td>
                        <td className="numeric">{getValue(ps)}</td>
                        <td><span className="badge badge-neutral">{getInterpretation(ps)}</span></td>
                    </tr>
                    <tr>
                        <td>Price/Book</td>
                        <td className="numeric">{getValue(pb)}</td>
                        <td><span className="badge badge-neutral">{getInterpretation(pb)}</span></td>
                    </tr>
                    <tr>
                        <td>EV/EBITDA</td>
                        <td className="numeric">{getValue(evEbitda)}</td>
                        <td><span className="badge badge-neutral">{getInterpretation(evEbitda)}</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
}
