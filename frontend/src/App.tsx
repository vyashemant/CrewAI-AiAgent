import { Routes, Route, useLocation } from 'react-router-dom';
import { Research } from './pages/Research';
import { History } from './pages/History';
import { DataSources } from './pages/DataSources';
import { Sidebar } from './components/layout/Sidebar';
import { TopNav } from './components/layout/TopNav';
import './index.css';

function App() {
  const location = useLocation();
  const path = location.pathname;
  let currentTab = 'new';
  if (path.startsWith('/history')) currentTab = 'history';
  else if (path.startsWith('/watchlist')) currentTab = 'watchlist';
  else if (path.startsWith('/data')) currentTab = 'data';

  return (
    <div className="app-shell">
      <Sidebar currentTab={currentTab} />
      
      <main className="main-content-wrapper">
        <TopNav />
        
        <div className="main-scroll-area">
          <Routes>
            <Route path="/" element={<Research />} />
            <Route path="/research" element={<Research />} />
            <Route path="/research/:jobId" element={<Research />} />
            <Route path="/history" element={<History />} />
            <Route path="/watchlist" element={<div style={{ padding: '2rem' }}><h2>Watchlist</h2><p>Watchlist view placeholder</p></div>} />
            <Route path="/data" element={<DataSources />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
