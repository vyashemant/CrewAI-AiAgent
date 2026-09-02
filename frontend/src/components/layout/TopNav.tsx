import { Bell, HelpCircle, Search, Settings, User } from 'lucide-react';

export function TopNav() {
    return (
        <header className="top-bar">
            <div className="search-container" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', background: 'var(--bg-primary)', padding: '0.375rem 0.75rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
                <Search size={16} />
                <input 
                    type="text" 
                    placeholder="Search tickers, companies..." 
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-primary)', outline: 'none', fontSize: '0.875rem', width: '200px' }}
                />
            </div>

            <nav className="top-nav">
                <div className="top-nav-item">Markets</div>
                <div className="top-nav-item">Screeners</div>
                <div className="top-nav-item">Portfolio</div>
                <div className="top-nav-item active">Analysis</div>
            </nav>

            <div className="top-actions">
                <button className="trade-btn">Trade</button>
                <button className="action-btn"><Bell size={18} /></button>
                <button className="action-btn"><Settings size={18} /></button>
                <button className="action-btn"><HelpCircle size={18} /></button>
                <button className="action-btn" style={{ marginLeft: '0.5rem' }}><User size={18} /></button>
            </div>
        </header>
    );
}
