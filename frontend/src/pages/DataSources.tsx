import { Database, ServerCog, Activity, Newspaper, BrainCircuit, LineChart } from 'lucide-react';

export function DataSources() {
    const sources = [
        {
            source: 'Yahoo Finance / yfinance',
            category: 'Market',
            purpose: 'Market prices, historical quotes, volumes, and standard metrics',
            status: 'Operational',
            icon: <Activity size={14} />
        },
        {
            source: 'SEC EDGAR XBRL',
            category: 'Financial',
            purpose: '10-K, 10-Q financial statements and footnotes',
            status: 'Operational',
            icon: <Database size={14} />
        },
        {
            source: 'Marketaux',
            category: 'News',
            purpose: 'Global financial news, sentiment analysis data',
            status: 'Operational',
            icon: <Newspaper size={14} />
        },
        {
            source: 'Python Metrics Engine',
            category: 'Analytics',
            purpose: 'Calculated ratios, DCF models, and performance metrics',
            status: 'Operational',
            icon: <ServerCog size={14} />
        },
        {
            source: 'Gemini 1.5 Pro',
            category: 'AI Analysis',
            purpose: 'Specialist research, risk modeling, and synthesis',
            status: 'Operational',
            icon: <BrainCircuit size={14} />
        },
        {
            source: 'Gemini 1.5 Pro',
            category: 'Strategy',
            purpose: 'Investment strategy, scenarios (Bull/Base/Bear)',
            status: 'Operational',
            icon: <LineChart size={14} />
        }
    ];

    return (
        <div style={{ padding: '2rem', maxWidth: '1440px', margin: '0 auto' }}>
            <div className="panel-header" style={{ marginBottom: '2rem' }}>
                <div className="panel-title" style={{ fontSize: '1.5rem', color: 'var(--text-primary)' }}>
                    <Database size={20} />
                    Data Sources Registry
                </div>
            </div>

            <div className="panel" style={{ padding: 0 }}>
                <table className="terminal-table" style={{ width: '100%' }}>
                    <thead>
                        <tr>
                            <th>Source</th>
                            <th>Category</th>
                            <th>Purpose</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sources.map((item, idx) => (
                            <tr key={idx}>
                                <td style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <span style={{ color: 'var(--text-secondary)' }}>{item.icon}</span>
                                    {item.source}
                                </td>
                                <td><span className="badge badge-neutral" style={{ fontSize: '0.625rem' }}>{item.category}</span></td>
                                <td style={{ color: 'var(--text-secondary)' }}>{item.purpose}</td>
                                <td>
                                    <span className={`badge ${item.status === 'Operational' ? 'badge-success' : 'badge-danger'}`} style={{ fontSize: '0.625rem' }}>
                                        {item.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
