import { Activity } from 'lucide-react';
import type { MarketSnapshot } from '../../types/api';
import { formatCurrency, formatLargeNumber, formatRatio, formatPercentagePoints } from '../../utils/formatters';

interface Props {
    snapshot: MarketSnapshot;
}

export function MarketSnapshotCard({ snapshot }: Props) {
    const { current_price, week_52_low, week_52_high, market_cap, beta, dividend_yield } = snapshot;

    let position = 50;
    if (current_price != null && week_52_low != null && week_52_high != null && week_52_high > week_52_low) {
        position = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100;
        position = Math.max(0, Math.min(100, position));
    }

    const getValue = (val: any, formatter: (v: any) => string) => {
        if (val === undefined || val === null) return 'Unavailable';
        return formatter(val);
    };

    return (
        <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="panel-header">
                <div className="panel-title">
                    <Activity size={16} />
                    Market Snapshot
                </div>
            </div>

            <div style={{ padding: '1rem 0', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div style={{ textAlign: 'center', fontSize: '0.625rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                    52-Week Price Range
                </div>

                <div style={{ position: 'relative', paddingBottom: '1.5rem', marginTop: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', alignItems: 'flex-end', fontFamily: 'var(--mono)' }}>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>{getValue(week_52_low, formatCurrency)}</span>
                            <span style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>52W Low</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'right' }}>
                            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>{getValue(week_52_high, formatCurrency)}</span>
                            <span style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>52W High</span>
                        </div>
                    </div>

                    <div className="range-track">
                        {(current_price != null && week_52_low != null && week_52_high != null) && (
                            <div className="range-marker" style={{ left: `${position}%` }}>
                                <div style={{ position: 'absolute', top: '-20px', left: '50%', transform: 'translateX(-50%)', whiteSpace: 'nowrap' }}>
                                    <span style={{ fontSize: '0.875rem', fontWeight: 600, fontFamily: 'var(--mono)', color: 'var(--text-primary)' }}>
                                        {getValue(current_price, formatCurrency)}
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1.25rem', marginTop: '0.5rem' }}>
                <div>
                    <div style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.25rem' }}>Market Cap</div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, fontFamily: 'var(--mono)', color: 'var(--text-primary)' }}>{getValue(market_cap, formatLargeNumber)}</div>
                </div>
                <div>
                    <div style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.25rem' }}>Beta</div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, fontFamily: 'var(--mono)', color: 'var(--text-primary)' }}>{getValue(beta, formatRatio)}</div>
                </div>
                <div>
                    <div style={{ fontSize: '0.625rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.25rem' }}>Div Yield</div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, fontFamily: 'var(--mono)', color: 'var(--text-primary)' }}>{getValue(dividend_yield, formatPercentagePoints)}</div>
                </div>
            </div>
        </div>
    );
}
