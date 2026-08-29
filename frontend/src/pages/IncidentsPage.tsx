import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { Shield, Brain, Send } from 'lucide-react';
import { cn } from '../lib/utils';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<any | null>(null);
  const [investigationReport, setInvestigationReport] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [queryResult, setQueryResult] = useState<string | null>(null);

  useEffect(() => {
    api.get('/incidents').then(res => setIncidents(res.data.incidents || []));
  }, []);

  const handleInvestigate = async (id: string) => {
    setLoading(true);
    try {
      const res = await api.post(`/soc/investigate/${id}`);
      setInvestigationReport(res.data.report);
      setQueryResult(null);
    } catch (e) {
      console.error(e);
      setInvestigationReport("Error generating investigation report.");
    }
    setLoading(false);
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    try {
      const res = await api.post(`/soc/query`, { query });
      setQueryResult(res.data.answer);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      {/* Incident List */}
      <div className="w-1/3 glass-panel overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-white/10 sticky top-0 bg-surface/90 backdrop-blur">
          <h2 className="text-xl font-bold">Active Incidents</h2>
        </div>
        <div className="flex-1 p-4 space-y-3">
          {incidents.map((inc) => (
            <div 
              key={inc.incident_id}
              onClick={() => {
                setSelectedIncident(inc);
                setInvestigationReport(null);
                setQueryResult(null);
              }}
              className={cn(
                "p-4 rounded-lg border cursor-pointer transition-all",
                selectedIncident?.incident_id === inc.incident_id 
                  ? "bg-primary/20 border-primary" 
                  : "bg-white/5 border-white/10 hover:bg-white/10"
              )}
            >
              <div className="flex justify-between items-start">
                <span className="font-mono text-sm text-muted">#{inc.incident_id.substring(0, 8)}</span>
                <span className={cn(
                  "px-2 py-0.5 rounded text-xs font-bold",
                  inc.severity === 'CRITICAL' ? 'bg-critical/20 text-critical' :
                  inc.severity === 'HIGH' ? 'bg-high/20 text-high' :
                  'bg-low/20 text-low'
                )}>{inc.severity}</span>
              </div>
              <h3 className="text-lg font-bold mt-2">{inc.target_host}</h3>
              <p className="text-sm text-muted mt-1">Risk Score: {inc.risk_score.toFixed(1)}</p>
            </div>
          ))}
          {incidents.length === 0 && <p className="text-muted p-4">No active incidents.</p>}
        </div>
      </div>

      {/* Investigation View */}
      <div className="flex-1 glass-panel flex flex-col overflow-hidden">
        {selectedIncident ? (
          <>
            <div className="p-6 border-b border-white/10 bg-surface/90 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <Shield className="text-primary" />
                  Host: {selectedIncident.target_host}
                </h2>
                <p className="text-muted text-sm mt-1 font-mono">Incident ID: {selectedIncident.incident_id}</p>
              </div>
              <button 
                onClick={() => handleInvestigate(selectedIncident.incident_id)}
                disabled={loading}
                className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50"
              >
                <Brain className="w-5 h-5" />
                {loading ? "Investigating..." : "Auto-Investigate (LLM)"}
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {!investigationReport ? (
                <div className="h-full flex items-center justify-center text-muted flex-col gap-4">
                  <Brain className="w-16 h-16 opacity-50" />
                  <p>Click "Auto-Investigate" to generate a RAG-grounded SOC report.</p>
                </div>
              ) : (
                <div className="prose prose-invert max-w-none">
                  {/* Super simple markdown renderer */}
                  {investigationReport.split('\n').map((line, i) => {
                    if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-bold text-white mt-6 mb-4">{line.replace('# ', '')}</h1>;
                    if (line.startsWith('**') && line.endsWith('**')) return <h3 key={i} className="text-lg font-bold text-primary mt-4 mb-2">{line.replace(/\*\*/g, '')}</h3>;
                    if (line.includes('[Observed]')) return <p key={i} className="mb-2"><span className="text-normal font-bold bg-normal/20 px-1 rounded mr-2">[Observed]</span>{line.replace('[Observed]', '')}</p>;
                    if (line.includes('[Inferred]')) return <p key={i} className="mb-2"><span className="text-high font-bold bg-high/20 px-1 rounded mr-2">[Inferred]</span>{line.replace('[Inferred]', '')}</p>;
                    if (line.includes('[Recommended]')) return <p key={i} className="mb-2"><span className="text-primary font-bold bg-primary/20 px-1 rounded mr-2">[Recommended]</span>{line.replace('[Recommended]', '')}</p>;
                    if (line.startsWith('- ')) return <li key={i} className="ml-4 text-muted">{line.substring(2)}</li>;
                    return <p key={i} className="text-muted mb-2">{line}</p>;
                  })}
                </div>
              )}
            </div>

            {/* Q&A Box */}
            {investigationReport && (
              <div className="p-4 border-t border-white/10 bg-surface/90">
                {queryResult && (
                  <div className="mb-4 p-4 bg-white/5 rounded-lg border border-white/10 text-sm">
                    <p className="font-bold text-primary mb-2">SOC Analyst Agent:</p>
                    <p className="text-text">{queryResult}</p>
                  </div>
                )}
                <form onSubmit={handleQuery} className="flex gap-2">
                  <input 
                    type="text" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a follow-up question grounded in retrieved evidence..."
                    className="flex-1 bg-background border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:border-primary text-text"
                  />
                  <button type="submit" className="bg-white/10 hover:bg-white/20 p-2 rounded-lg transition-colors">
                    <Send className="w-5 h-5 text-primary" />
                  </button>
                </form>
              </div>
            )}
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-muted">
            Select an incident from the list to begin investigation.
          </div>
        )}
      </div>
    </div>
  );
}
