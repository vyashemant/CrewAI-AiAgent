
import type { DataSources  } from '../../types/api';

interface Props {
    sources: DataSources;
}

export function DataSourcesSection({ sources }: Props) {
    if (!sources) return null;

    return (
        <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #e2e8f0', color: '#64748b', fontSize: '0.85rem' }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Data Sources</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                <span><strong>Market Data:</strong> {sources.market_data}</span>
                <span><strong>Financials:</strong> {sources.financial_statements}</span>
                <span><strong>News:</strong> {sources.news}</span>
                <span><strong>Metrics:</strong> {sources.metrics}</span>
                <span><strong>Specialist:</strong> {sources.specialist_analysis}</span>
                <span><strong>Strategy:</strong> {sources.investment_strategy}</span>
            </div>
        </div>
    );
}
