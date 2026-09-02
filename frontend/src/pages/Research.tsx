import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Terminal, Database, BrainCircuit, Activity } from 'lucide-react';
import { ApiClient } from '../api/client';
import { useResearchPolling } from '../hooks/useResearchPolling';
import { ResearchDashboard } from '../components/dashboard/ResearchDashboard';

export function Research() {
    const { jobId: urlJobId } = useParams<{ jobId: string }>();
    const navigate = useNavigate();
    
    const [company, setCompany] = useState('');
    const [ticker, setTicker] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const { jobId, setJobId, status, result, error, setError } = useResearchPolling(urlJobId || null);

    useEffect(() => {
        if (urlJobId !== jobId) {
            setJobId(urlJobId || null);
        }
    }, [urlJobId, setJobId, jobId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);

        try {
            const response = await ApiClient.submitResearch({ company, ticker });
            navigate(`/research/${response.job_id}`);
        } catch (err: any) {
            setError(err.message || 'Failed to submit research request.');
        } finally {
            setSubmitting(false);
        }
    };

    if (jobId) {
        return (
            <div style={{ maxWidth: '1440px', margin: '0 auto' }}>
                <div className="panel" style={{ marginBottom: '1.5rem', backgroundColor: 'var(--bg-panel)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div>
                            <div style={{ fontFamily: 'var(--mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>JOB ID: {jobId}</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.5rem' }}>
                                <span className={`badge ${status === 'completed' ? 'badge-success' : status === 'failed' ? 'badge-danger' : 'badge-warning'}`}>
                                    {status ? status.toUpperCase() : 'LOADING'}
                                </span>
                                {(status === 'queued' || status === 'running') && (
                                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                        Research is in progress. This may take a few minutes...
                                    </span>
                                )}
                            </div>
                        </div>
                        <button className="action-btn" onClick={() => navigate('/research')} style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--bg-hover)', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.75rem' }}>
                            START NEW
                        </button>
                    </div>
                </div>

                {error && <div className="badge badge-danger" style={{ display: 'block', padding: '1rem', marginBottom: '1.5rem' }}>{error}</div>}
                
                {status === 'failed' && (
                    <div className="badge badge-danger" style={{ display: 'block', padding: '1rem', marginBottom: '1.5rem' }}>
                        Research job failed: {result?.error || 'Unknown error'}
                    </div>
                )}

                {status === 'completed' && result?.result && (
                    <ResearchDashboard report={result.result} />
                )}
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', paddingTop: '4rem' }}>
            <div style={{ width: '100%', maxWidth: '480px' }}>
                <div style={{ marginBottom: '2rem' }}>
                    <h1 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Terminal size={24} /> New Research
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        Initialize an AI-driven public company equity research sequence.
                    </p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div className="panel" style={{ padding: 0 }}>
                        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)' }}>
                            <label htmlFor="company" style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                                Company Name
                            </label>
                            <input
                                id="company"
                                type="text"
                                placeholder="e.g. Apple Inc."
                                value={company}
                                onChange={e => setCompany(e.target.value)}
                                required
                                style={{
                                    width: '100%', background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '1rem', outline: 'none'
                                }}
                            />
                        </div>
                        <div style={{ padding: '1rem 1.25rem' }}>
                            <label htmlFor="ticker" style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                                Ticker Symbol
                            </label>
                            <input
                                id="ticker"
                                type="text"
                                placeholder="e.g. AAPL"
                                value={ticker}
                                onChange={e => setTicker(e.target.value.toUpperCase())}
                                required
                                style={{
                                    width: '100%', background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: '1rem', outline: 'none'
                                }}
                            />
                        </div>
                    </div>

                    <button type="submit" disabled={submitting} className="trade-btn" style={{ width: '100%', padding: '0.875rem', fontSize: '0.875rem' }}>
                        {submitting ? 'INITIALIZING...' : 'START RESEARCH'}
                    </button>
                    {error && <div className="badge badge-danger" style={{ display: 'block', padding: '1rem', textAlign: 'center' }}>{error}</div>}
                </form>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid var(--border)' }}>
                    <div style={{ textAlign: 'center', flex: 1 }}>
                        <Activity size={16} color="var(--text-secondary)" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Market Data</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>Yahoo Finance</div>
                    </div>
                    <div style={{ textAlign: 'center', flex: 1 }}>
                        <Database size={16} color="var(--text-secondary)" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Financial Data</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>SEC EDGAR</div>
                    </div>
                    <div style={{ textAlign: 'center', flex: 1 }}>
                        <BrainCircuit size={16} color="var(--text-secondary)" style={{ marginBottom: '0.5rem' }} />
                        <div style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>AI Analysis</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)' }}>Google Gemini</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
