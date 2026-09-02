import { Activity, Clock, Compass, Database, LifeBuoy, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SidebarProps {
    currentTab: string;
}

export function Sidebar({ currentTab }: SidebarProps) {
    const navigate = useNavigate();
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="brand-title">Alpha Terminal</div>
                <div className="brand-subtitle">AI Research</div>
            </div>
            
            <nav className="sidebar-nav">
                <div 
                    className={`nav-item ${currentTab === 'new' ? 'active' : ''}`}
                    onClick={() => navigate('/')}
                >
                    <Compass size={18} />
                    <span>New Research</span>
                </div>
                <div 
                    className={`nav-item ${currentTab === 'history' ? 'active' : ''}`}
                    onClick={() => navigate('/history')}
                >
                    <Clock size={18} />
                    <span>History</span>
                </div>
                <div 
                    className={`nav-item ${currentTab === 'watchlist' ? 'active' : ''}`}
                    onClick={() => navigate('/watchlist')}
                >
                    <Activity size={18} />
                    <span>Watchlist</span>
                </div>
                <div 
                    className={`nav-item ${currentTab === 'data' ? 'active' : ''}`}
                    onClick={() => navigate('/data')}
                >
                    <Database size={18} />
                    <span>Data Sources</span>
                </div>
            </nav>

            <div className="sidebar-footer">
                <div className="nav-item">
                    <ShieldAlert size={18} />
                    <span>Security</span>
                </div>
                <div className="nav-item">
                    <LifeBuoy size={18} />
                    <span>Support</span>
                </div>
            </div>
        </aside>
    );
}
