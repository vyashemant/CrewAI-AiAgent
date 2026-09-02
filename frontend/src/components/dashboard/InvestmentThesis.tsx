import { AlertTriangle, TrendingUp, TrendingDown, Target } from 'lucide-react';
import type { InvestmentStrategy } from '../../types/api';

interface Props {
    strategy: InvestmentStrategy;
}

export function InvestmentThesis({ strategy }: Props) {
    return (
        <div className="panel" style={{ marginBottom: '1.5rem' }}>
            <div className="panel-header">
                <div className="panel-title">
                    <Target size={16} />
                    Investment Thesis
                </div>
            </div>
            
            <div className="thesis-text">
                "{strategy.investment_thesis}"
            </div>

            <div className="grid-3" style={{ marginTop: '2rem' }}>
                <div>
                    <div className="panel-title" style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                        <TrendingUp size={14} /> Key Catalysts
                    </div>
                    <ul className="compact-list">
                        {strategy.key_catalysts.map((cat, i) => (
                            <li key={i}>
                                <span className="list-number">{(i + 1).toString().padStart(2, '0')}</span>
                                <span>{cat}</span>
                            </li>
                        ))}
                    </ul>
                </div>
                
                <div>
                    <div className="panel-title" style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                        <AlertTriangle size={14} /> Key Risks
                    </div>
                    <ul className="compact-list">
                        {strategy.key_risks.map((risk, i) => (
                            <li key={i}>
                                <span className="list-number">{(i + 1).toString().padStart(2, '0')}</span>
                                <span>{risk}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                <div>
                    <div className="panel-title" style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                        <TrendingDown size={14} /> Thesis Change Triggers
                    </div>
                    <ul className="compact-list">
                        {strategy.thesis_change_triggers.map((trigger, i) => (
                            <li key={i}>
                                <span className="list-number">{(i + 1).toString().padStart(2, '0')}</span>
                                <span>{trigger}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {strategy.contradictions_detected && (
                <div style={{ marginTop: '1.5rem', padding: '0.75rem 1rem', backgroundColor: 'var(--warning-bg)', border: '1px solid var(--warning)', borderRadius: '4px' }}>
                    <details>
                        <summary style={{ color: 'var(--warning)', fontWeight: '600', cursor: 'pointer', outline: 'none', fontSize: '0.875rem' }}>
                            ⚠ Research Notes / Data Consistency Issues Detected
                        </summary>
                        <div style={{ color: 'var(--text-primary)', fontSize: '0.875rem', marginTop: '0.75rem', lineHeight: 1.5 }}>
                            {strategy.contradictions_detected}
                        </div>
                    </details>
                </div>
            )}
        </div>
    );
}
