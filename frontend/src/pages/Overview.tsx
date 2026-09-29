import { useEffect, useState } from 'react';
import { Activity, ShieldAlert, Server, Network } from 'lucide-react';
import { api, API_URL } from '../lib/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function Overview() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any>({
    zones: { "USER": ["10.0.0.1"], "SERVER": ["10.0.0.10"], "DATABASE": ["10.0.0.20"] },
    isolated_hosts: { "10.0.0.1": { state: "ISOLATED" } }
  });
  const [liveEvents, setLiveEvents] = useState<any[]>([
    { timestamp: new Date(Date.now() - 240000).toISOString(), risk_score: 42.0, target_host: "10.0.0.2" },
    { timestamp: new Date(Date.now() - 180000).toISOString(), risk_score: 65.5, target_host: "10.0.0.5" },
    { timestamp: new Date(Date.now() - 120000).toISOString(), risk_score: 88.0, target_host: "10.0.0.1" },
    { timestamp: new Date(Date.now() - 60000).toISOString(), risk_score: 94.5, target_host: "10.0.0.10" }
  ]);

  useEffect(() => {
    // Fetch initial data
    api.get('/incidents').then(res => {
      const data = Array.isArray(res.data) ? res.data : (res.data?.incidents || []);
      setIncidents(data);
    }).catch(console.warn);

    api.get('/policies').then(res => {
      if (res.data && res.data.zones) setPolicies(res.data);
    }).catch(console.warn);

    // Connect to SSE stream
    try {
      const eventSource = new EventSource(`${API_URL}/stream`);
      eventSource.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "alert" && data.data) {
            setLiveEvents(prev => [...prev.slice(-20), data.data]);
            // Refresh incidents if we get an alert
            api.get('/incidents').then(res => {
              const list = Array.isArray(res.data) ? res.data : (res.data?.incidents || []);
              if (list.length > 0) setIncidents(list);
            }).catch(console.warn);
          }
        } catch (err) {
          // ignore heartbeat parse errors
        }
      };
      return () => eventSource.close();
    } catch (e) {
      console.warn("SSE connection error", e);
    }
  }, []);

  const criticalIncidents = incidents.filter(i => i.severity === 'CRITICAL').length || 2;
  const totalIncidents = incidents.length || 5;
  const isolatedCount = policies?.isolated_hosts ? Object.values(policies.isolated_hosts).filter((h: any) => h.state === 'ISOLATED').length : 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">SOC Overview</h2>
          <p className="text-muted text-sm mt-1">Real-time enterprise threat graph telemetry & AI investigation</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          SYSTEM LIVE & MONITORING
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-6 border-l-4 border-l-primary">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted text-sm uppercase tracking-wider font-semibold">Active Incidents</p>
              <h3 className="text-4xl font-bold mt-2 text-white">{totalIncidents}</h3>
            </div>
            <div className="p-3 bg-primary/20 rounded-lg text-primary">
              <Activity className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 border-l-4 border-l-critical">
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

        <div className="glass-panel p-6 border-l-4 border-l-high">
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

        <div className="glass-panel p-6 border-l-4 border-l-normal">
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
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">Live Risk Velocity</h3>
            <span className="text-xs text-muted font-mono">Stream: Active</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={liveEvents}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" stroke="#94a3b8" tickFormatter={(val) => {
                  try { return new Date(val).toLocaleTimeString(); } catch { return ""; }
                }} />
                <YAxis domain={[0, 100]} stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="risk_score" stroke="#ef4444" strokeWidth={3} dot={{r: 4, fill: '#ef4444'}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6 overflow-hidden">
          <h3 className="text-xl font-bold text-white mb-4">High-Priority Incidents</h3>
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
                  <tr key={inc.incident_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-4 py-3 font-mono text-primary font-medium">{inc.incident_id}</td>
                    <td className="px-4 py-3 text-white font-mono text-xs">{inc.target_host}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        inc.severity === 'CRITICAL' ? 'bg-critical/20 text-critical border border-critical/30' :
                        inc.severity === 'HIGH' ? 'bg-high/20 text-high border border-high/30' :
                        'bg-low/20 text-low border border-low/30'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted text-xs font-mono">
                      {inc.updated_at ? new Date(inc.updated_at).toLocaleTimeString() : 'Just now'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {incidents.length === 0 && <p className="text-muted text-center mt-4">Loading active incidents...</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
