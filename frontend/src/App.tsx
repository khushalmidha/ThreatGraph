import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity, ShieldAlert, Network, Shield, Home } from 'lucide-react';
import Overview from './pages/Overview';
import NetworkGraphPage from './pages/NetworkGraphPage';
import IncidentsPage from './pages/IncidentsPage';
import ContainmentPage from './pages/ContainmentPage';

function Sidebar() {
  return (
    <div className="w-64 bg-surface border-r border-white/10 flex flex-col h-screen">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
          <ShieldAlert className="w-8 h-8" />
          NetRaptor-X
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        <Link to="/" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 text-muted hover:text-white transition-colors">
          <Home className="w-5 h-5" />
          Overview
        </Link>
        <Link to="/graph" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 text-muted hover:text-white transition-colors">
          <Network className="w-5 h-5" />
          Network Graph
        </Link>
        <Link to="/incidents" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 text-muted hover:text-white transition-colors">
          <Activity className="w-5 h-5" />
          SOC Analyst
        </Link>
        <Link to="/containment" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 text-muted hover:text-white transition-colors">
          <Shield className="w-5 h-5" />
          Containment
        </Link>
      </nav>
      <div className="p-4 border-t border-white/10 text-xs text-muted">
        System Health: Online
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-background text-text overflow-hidden font-sans">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8 relative">
          {/* Background glows */}
          <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
          <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-critical/10 blur-[120px] pointer-events-none" />
          
          <div className="relative z-10">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/graph" element={<NetworkGraphPage />} />
              <Route path="/incidents" element={<IncidentsPage />} />
              <Route path="/containment" element={<ContainmentPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
