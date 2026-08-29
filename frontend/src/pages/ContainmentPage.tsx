import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { Shield, ShieldAlert, CheckCircle2, Lock } from 'lucide-react';

export default function ContainmentPage() {
  const [policies, setPolicies] = useState<any>(null);
  const [loadingHost, setLoadingHost] = useState<string | null>(null);

  const fetchPolicies = () => {
    api.get('/policies').then(res => setPolicies(res.data));
  };

  useEffect(() => {
    fetchPolicies();
    // Poll for simplicity, though SSE is better
    const interval = setInterval(fetchPolicies, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (host: string, action: 'isolate' | 'release') => {
    setLoadingHost(host);
    try {
      await api.post(`/containment/${action}/${host}`);
      fetchPolicies();
    } catch (e) {
      console.error(e);
      alert("Action failed. Check console or API permissions.");
    }
    setLoadingHost(null);
  };

  if (!policies) return <div className="p-8 text-muted">Loading policies...</div>;

  const allHosts = new Set<string>();
  Object.values(policies.zones).forEach((hosts: any) => hosts.forEach((h: string) => allHosts.add(h)));
  const hostList = Array.from(allHosts);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center gap-3 mb-8">
        <Shield className="w-8 h-8 text-primary" />
        <h2 className="text-3xl font-bold text-white">Network Containment</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-panel p-6 border-l-4 border-l-primary">
          <h3 className="text-lg font-bold text-white">Zone Model</h3>
          <p className="text-muted text-sm mt-1">Zero-trust micro-segmentation active.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {Object.keys(policies.zones).map(zone => (
              <span key={zone} className="px-2 py-1 bg-white/10 rounded text-xs font-mono">{zone}</span>
            ))}
          </div>
        </div>
        <div className="glass-panel p-6 border-l-4 border-l-critical">
          <h3 className="text-lg font-bold text-white">Isolated Hosts</h3>
          <p className="text-muted text-sm mt-1">Currently quarantined endpoints.</p>
          <h2 className="text-3xl font-bold text-critical mt-2">
            {Object.values(policies.isolated_hosts || {}).filter((h: any) => h.state === 'ISOLATED').length}
          </h2>
        </div>
        <div className="glass-panel p-6 border-l-4 border-l-normal">
          <h3 className="text-lg font-bold text-white">Enforcement Mode</h3>
          <p className="text-muted text-sm mt-1">Manual Analyst Approval Required</p>
          <div className="mt-4 flex items-center gap-2 text-normal font-bold">
            <Lock className="w-4 h-4" /> SECURE
          </div>
        </div>
      </div>

      <div className="glass-panel overflow-hidden">
        <div className="p-4 border-b border-white/10 bg-surface/50">
          <h3 className="text-xl font-bold text-white">Endpoint Enforcement</h3>
        </div>
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted uppercase bg-white/5 border-b border-white/10">
            <tr>
              <th className="px-6 py-4">Host IP</th>
              <th className="px-6 py-4">Zone</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {hostList.map(host => {
              const zoneEntry = Object.entries(policies.zones).find((entry: any) => entry[1].includes(host));
              const zone = zoneEntry ? zoneEntry[0] : 'UNKNOWN';
              const isIsolated = policies.isolated_hosts?.[host]?.state === 'ISOLATED';
              const isLoading = loadingHost === host;

              return (
                <tr key={host} className="border-b border-white/5 hover:bg-white/5">
                  <td className="px-6 py-4 font-mono text-white">{host}</td>
                  <td className="px-6 py-4 text-muted">{zone}</td>
                  <td className="px-6 py-4">
                    {isIsolated ? (
                      <span className="flex items-center gap-2 text-critical font-bold">
                        <ShieldAlert className="w-4 h-4" /> ISOLATED
                      </span>
                    ) : (
                      <span className="flex items-center gap-2 text-normal">
                        <CheckCircle2 className="w-4 h-4" /> ACTIVE
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {isIsolated ? (
                      <button 
                        onClick={() => handleAction(host, 'release')}
                        disabled={isLoading}
                        className="px-4 py-2 bg-normal/20 hover:bg-normal/30 text-normal rounded font-bold transition-colors disabled:opacity-50"
                      >
                        {isLoading ? "Wait..." : "Release"}
                      </button>
                    ) : (
                      <button 
                        onClick={() => handleAction(host, 'isolate')}
                        disabled={isLoading}
                        className="px-4 py-2 bg-critical/20 hover:bg-critical/30 text-critical rounded font-bold transition-colors disabled:opacity-50"
                      >
                        {isLoading ? "Wait..." : "Isolate"}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
