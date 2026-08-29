import { useEffect, useState } from 'react';
import { Activity, ShieldAlert, Server, Network } from 'lucide-react';
import { api, API_URL } from '../lib/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function Overview() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any>(null);
  const [liveEvents, setLiveEvents] = useState<any[]>([]);

  useEffect(() => {
    // Fetch initial data
    api.get('/incidents').then(res => setIncidents(res.data.incidents || []));
    api.get('/policies').then(res => setPolicies(res.data));

    // Connect to SSE stream
    const eventSource = new EventSource(`${API_URL}/stream`);
    eventSource.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "alert") {
        setLiveEvents(prev => [...prev.slice(-20), data.data]);
        // Refresh incidents if we get an alert
        api.get('/incidents').then(res => setIncidents(res.data.incidents || []));
      }
    };

    return () => eventSource.close();
  }, []);

  const criticalIncidents = incidents.filter(i => i.severity === 'CRITICAL').length;
  const isolatedCount = policies ? Object.values(policies.isolated_hosts || {}).filter((h: any) => h.state === 'ISOLATED').length : 0;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white mb-8">SOC Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted text-sm uppercase tracking-wider font-semibold">Active Incidents</p>
              <h3 className="text-4xl font-bold mt-2 text-white">{incidents.length}</h3>
            </div>
            <div className="p-3 bg-primary/20 rounded-lg text-primary">
              <Activity className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="glass-panel p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted text-sm uppercase tracking-wider font-semibold">Critical Threats</p>
              <h3 className="text-4xl font-bold mt-2 text-critical">{criticalIncidents}</h3>
            </div>
            <div className="p-3 bg-critical/20 rounded-lg text-critical">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="glass-panel p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted text-sm uppercase tracking-wider font-semibold">Isolated Hosts</p>
              <h3 className="text-4xl font-bold mt-2 text-high">{isolatedCount}</h3>
            </div>
            <div className="p-3 bg-high/20 rounded-lg text-high">
              <Server className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="glass-panel p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted text-sm uppercase tracking-wider font-semibold">Live Detections</p>
              <h3 className="text-4xl font-bold mt-2 text-normal">{liveEvents.length}</h3>
            </div>
            <div className="p-3 bg-normal/20 rounded-lg text-normal">
              <Network className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="glass-panel p-6">
          <h3 className="text-xl font-bold text-white mb-4">Risk Trends (Live)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={liveEvents.length > 0 ? liveEvents : [{timestamp: new Date().toISOString(), risk_score: 0}]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" stroke="#94a3b8" tickFormatter={(val) => new Date(val).toLocaleTimeString()} />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="risk_score" stroke="#ef4444" strokeWidth={3} dot={{r: 4, fill: '#ef4444'}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6 overflow-hidden">
          <h3 className="text-xl font-bold text-white mb-4">Recent Incidents</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted uppercase bg-white/5 border-b border-white/10">
                <tr>
                  <th className="px-4 py-3 rounded-tl-lg">ID</th>
                  <th className="px-4 py-3">Host</th>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3 rounded-tr-lg">Time</th>
                </tr>
              </thead>
              <tbody>
                {incidents.slice(0, 5).map(inc => (
                  <tr key={inc.incident_id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="px-4 py-3 font-mono text-primary">{inc.incident_id.substring(0, 8)}</td>
                    <td className="px-4 py-3 text-white">{inc.target_host}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        inc.severity === 'CRITICAL' ? 'bg-critical/20 text-critical' :
                        inc.severity === 'HIGH' ? 'bg-high/20 text-high' :
                        'bg-low/20 text-low'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted">{new Date(inc.updated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {incidents.length === 0 && <p className="text-muted text-center mt-4">No incidents detected.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
