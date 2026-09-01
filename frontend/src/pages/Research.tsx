import React, { useState } from 'react';
import { ApiClient } from '../api/client';
import { useResearchPolling } from '../hooks/useResearchPolling';
import '../styles/main.css';

export function Research() {
    const [company, setCompany] = useState('');
    const [ticker, setTicker] = useState('');
    const [submitting, setSubmitting] = useState(false);
    
    const { jobId, setJobId, status, result, error, setError } = useResearchPolling(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);
        setJobId(null);
        
        try {
            const response = await ApiClient.submitResearch({ company, ticker });
            setJobId(response.job_id);
        } catch (err: any) {
            setError(err.message || 'Failed to submit research request.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="research-container">
            <header className="research-header">
                <h1>AI Investment Research</h1>
                <p>Enter a company and ticker to generate a comprehensive investment report.</p>
            </header>

            {!jobId && (
                <form className="research-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="company">Company Name</label>
                        <input 
                            id="company"
                            type="text" 
                            placeholder="e.g. Apple Inc." 
                            value={company} 
                            onChange={e => setCompany(e.target.value)} 
                            required 
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="ticker">Ticker Symbol</label>
                        <input 
                            id="ticker"
                            type="text" 
                            placeholder="e.g. AAPL" 
                            value={ticker} 
                            onChange={e => setTicker(e.target.value.toUpperCase())} 
                            required 
                        />
                    </div>
                    <button type="submit" disabled={submitting}>
                        {submitting ? 'Submitting...' : 'Start Research'}
                    </button>
                    {error && <div className="error-message">{error}</div>}
                </form>
            )}

            {jobId && (
                <div className="status-container">
                    <h2>Research Job Status</h2>
                    <p className="job-id">Job ID: {jobId}</p>
                    
                    <div className={`status-badge status-${status}`}>
                        {status ? status.toUpperCase() : 'INITIALIZING'}
                    </div>

                    {(status === 'queued' || status === 'running') && (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Research is in progress. This may take a minute...</p>
                        </div>
                    )}

                    {error && <div className="error-message">{error}</div>}

                    {status === 'failed' && (
                        <div className="error-message">
                            <p>Research job failed: {result?.error || 'Unknown error'}</p>
                            <button onClick={() => setJobId(null)}>Try Again</button>
                        </div>
                    )}

                    {status === 'completed' && result?.result && (
                        <div className="result-summary">
                            <h3>Research Completed</h3>
                            <div className="summary-card">
                                <div className="summary-row">
                                    <span className="label">Company:</span>
                                    <span className="value">{result.result.company}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Ticker:</span>
                                    <span className="value">{result.result.ticker}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Market Date:</span>
                                    <span className="value">{result.result.research_date}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Recommendation:</span>
                                    <span className={`value rec-${result.result.investment_strategy.recommendation.toLowerCase()}`}>
                                        {result.result.investment_strategy.recommendation}
                                    </span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Confidence:</span>
                                    <span className="value">{result.result.investment_strategy.confidence}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Current Price:</span>
                                    <span className="value">{result.result.market_snapshot?.current_price ?? 'Unavailable'}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Market Cap:</span>
                                    <span className="value">{result.result.market_snapshot?.market_cap ?? 'Unavailable'}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Revenue:</span>
                                    <span className="value">{result.result.financial_summary?.revenue ?? 'Unavailable'}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Net Income:</span>
                                    <span className="value">{result.result.financial_summary?.net_income ?? 'Unavailable'}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Historical Revenue CAGR:</span>
                                    <span className="value">{result.result.trend_summary?.revenue_cagr ?? 'Unavailable'}</span>
                                </div>
                                <div className="summary-row">
                                    <span className="label">Historical Net Income CAGR:</span>
                                    <span className="value">{result.result.trend_summary?.net_income_cagr ?? 'Unavailable'}</span>
                                </div>
                            </div>

                            <div className="lists-container" style={{ textAlign: 'left', marginBottom: '2rem' }}>
                                <h4>Major Risks</h4>
                                <ul>
                                    {result.result.investment_strategy.key_risks.map((risk, idx) => (
                                        <li key={idx} style={{ marginBottom: '0.5rem' }}>{risk}</li>
                                    ))}
                                </ul>

                                <h4>Major Catalysts</h4>
                                <ul>
                                    {result.result.investment_strategy.key_catalysts.map((catalyst, idx) => (
                                        <li key={idx} style={{ marginBottom: '0.5rem' }}>{catalyst}</li>
                                    ))}
                                </ul>
                            </div>
                            <button className="new-research-btn" onClick={() => {
                                setJobId(null);
                                setCompany('');
                                setTicker('');
                            }}>New Research</button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
