import { Routes, Route, useLocation } from 'react-router-dom';
import { Research } from './pages/Research';
import { History } from './pages/History';
import { DataSources } from './pages/DataSources';
import { AuthPage } from './pages/AuthPage';
import { Sidebar } from './components/layout/Sidebar';
import { TopNav } from './components/layout/TopNav';
import { ProtectedRoute } from './components/ProtectedRoute';
import './index.css';

function App() {
  const location = useLocation();
  const path = location.pathname;
  let currentTab = 'new';
  if (path.startsWith('/history')) currentTab = 'history';
  else if (path.startsWith('/watchlist')) currentTab = 'watchlist';
  else if (path.startsWith('/data')) currentTab = 'data';

  // If the user is on /auth but they are already logged in, they shouldn't see Sidebar.
  // Actually, we can just render AuthPage standalone when on /auth.
  if (path === '/auth') {
    return (
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
      </Routes>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar currentTab={currentTab} />
      
      <main className="main-content-wrapper">
        <TopNav />
        
        <div className="main-scroll-area">
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Research />} />
              <Route path="/research" element={<Research />} />
              <Route path="/research/:jobId" element={<Research />} />
              <Route path="/history" element={<History />} />
              <Route path="/watchlist" element={<div style={{ padding: '2rem' }}><h2>Watchlist</h2><p>Watchlist view placeholder</p></div>} />
              <Route path="/data" element={<DataSources />} />
            </Route>
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
