import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock } from 'lucide-react';
import { ApiClient } from '../api/client';
import type { ResearchHistoryItem } from '../types/api';
import { formatDate } from '../utils/formatters';

export function History() {
    const [history, setHistory] = useState<ResearchHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await ApiClient.getResearchHistory();
                setHistory(response.research);
            } catch (err: any) {
                setError(err.message || 'Failed to fetch history');
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    const completedCount = history.filter(h => h.status === 'completed').length;
    const failedCount = history.filter(h => h.status === 'failed').length;
    const runningCount = history.filter(h => h.status === 'running' || h.status === 'queued').length;

    return (
        <div style={{ padding: '2rem', maxWidth: '1440px', margin: '0 auto', width: '100%' }}>
            <div className="terminal-header" style={{ marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <div className="panel-title" style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                        <Clock size={20} />
                        RESEARCH HISTORY
                    </div>
                    {!loading && !error && history.length > 0 && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', gap: '1rem', fontFamily: 'var(--mono)' }}>
                            <span>{history.length} total jobs</span>
                            <span style={{ color: 'var(--success)' }}>{completedCount} completed</span>
                            <span style={{ color: 'var(--danger)' }}>{failedCount} failed</span>
                            <span style={{ color: 'var(--warning)' }}>{runningCount} running</span>
                        </div>
                    )}
                </div>
            </div>

            {loading ? (
                <div className="panel" style={{ color: 'var(--text-secondary)', padding: '2rem', textAlign: 'center' }}>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: '0.875rem' }}>Loading history data...</div>
                </div>
            ) : error ? (
                <div className="panel" style={{ color: 'var(--danger)', borderLeft: '2px solid var(--danger)', padding: '1rem' }}>
                    <div style={{ fontFamily: 'var(--mono)', fontSize: '0.875rem' }}>ERROR: {error}</div>
                </div>
            ) : history.length === 0 ? (
                <div className="panel" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>NO RESEARCH YET</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Start your first company research to populate this workspace.</div>
                </div>
            ) : (
                <div className="panel" style={{ padding: 0, overflowX: 'auto' }}>
                    <table className="terminal-table history-table" style={{ width: '100%', tableLayout: 'fixed' }}>
                        <thead>
                            <tr>
                                <th style={{ width: '18%', textAlign: 'left' }}>Date</th>
                                <th style={{ width: '18%', textAlign: 'left' }}>Company</th>
                                <th style={{ width: '10%', textAlign: 'left' }}>Ticker</th>
                                <th style={{ width: '14%', textAlign: 'center' }}>Status</th>
                                <th style={{ width: '25%', textAlign: 'left' }}>Job ID</th>
                                <th style={{ width: '15%', textAlign: 'right' }}>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map((item) => (
                                <tr key={item.job_id} className="history-row" style={{ borderBottom: '1px solid var(--border-light)' }}>
                                    <td style={{ fontSize: '0.875rem', textAlign: 'left' }}>{formatDate(item.created_at)}</td>
                                    <td style={{ fontWeight: 600, textAlign: 'left', color: 'var(--text-primary)' }}>{item.company}</td>
                                    <td style={{ textAlign: 'left' }}>
                                        <span className="badge badge-neutral" style={{ fontSize: '0.625rem' }}>{item.ticker}</span>
                                    </td>
                                    <td style={{ textAlign: 'center' }}>
                                        <span className={`badge ${item.status === 'completed' ? 'badge-success' : item.status === 'failed' ? 'badge-danger' : 'badge-warning'}`} style={{ fontSize: '0.625rem' }}>
                                            {item.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td style={{ fontFamily: 'var(--mono)', fontSize: '0.875rem', color: 'var(--text-muted)', textAlign: 'left', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {item.job_id.slice(0, 12)}...
                                    </td>
                                    <td style={{ textAlign: 'right' }}>
                                        <button 
                                            className="action-btn" 
                                            onClick={() => navigate(`/research/${item.job_id}`)}
                                            style={{ 
                                                fontSize: '0.75rem', 
                                                fontWeight: 600, 
                                                color: 'var(--accent-light)', 
                                                border: '1px solid var(--border)', 
                                                padding: '0.25rem 0.75rem', 
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            VIEW →
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
