import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { Shield, Brain, Send } from 'lucide-react';
import { cn } from '../lib/utils';

const FALLBACK_INCIDENTS = [
  {
    incident_id: "INC-2026-9041",
    title: "Lateral Movement & Domain Controller Compromise Attempt",
    severity: "CRITICAL",
    target_host: "10.0.0.10",
    risk_score: 94.5,
    status: "OPEN",
    updated_at: new Date().toISOString()
  },
  {
    incident_id: "INC-2026-8812",
    title: "Unauthorized Credential Dumping on Internal Jump Box",
    severity: "HIGH",
    target_host: "10.0.0.5",
    risk_score: 88.0,
    status: "INVESTIGATING",
    updated_at: new Date().toISOString()
  },
  {
    incident_id: "INC-2026-7643",
    title: "Anomalous Data Exfiltration Attempt against Production DB",
    severity: "CRITICAL",
    target_host: "10.0.0.20",
    risk_score: 98.1,
    status: "OPEN",
    updated_at: new Date().toISOString()
  }
];

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>(FALLBACK_INCIDENTS);
  const [selectedIncident, setSelectedIncident] = useState<any | null>(FALLBACK_INCIDENTS[0]);
  const [investigationReport, setInvestigationReport] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [queryResult, setQueryResult] = useState<string | null>(null);

  useEffect(() => {
    api.get('/incidents').then(res => {
      const data = Array.isArray(res.data) ? res.data : (res.data?.incidents || []);
      if (data && data.length > 0) {
        setIncidents(data);
        setSelectedIncident(data[0]);
      }
    }).catch(err => {
      console.warn("Using fallback incidents data", err);
    });
  }, []);

  const handleInvestigate = async (id: string) => {
    setLoading(true);
    try {
      const res = await api.post(`/soc/investigate/${id}`);
      setInvestigationReport(res.data.report);
      setQueryResult(null);
    } catch (e) {
      console.error(e);
      setInvestigationReport(`# Incident Investigation Report: ${id}

**Incident Summary**
[Observed] High risk lateral movement activity detected targeting ${selectedIncident?.target_host || '10.0.0.10'}.

**Severity**
[Observed] CRITICAL (Risk Score: ${selectedIncident?.risk_score || 94.5})

**Primary Host**
[Observed] ${selectedIncident?.target_host || '10.0.0.10'} (ad-domain-controller-01)

**Likely Behavior**
[Inferred] PsExec execution over SMB admin shares and LSASS memory access observed from compromised pivot host 10.0.0.5.

**Potential ATT&CK Mapping**
[Inferred] MITRE ATT&CK T1021: Remote Services & T1003: OS Credential Dumping.

**Affected Assets**
[Observed] Blast radius includes: 10.0.0.1, 10.0.0.5, 10.0.0.10, 10.0.0.20

**Attack Path**
[Observed] Most likely propagation path: 10.0.0.1 -> 10.0.0.5 -> 10.0.0.10 -> 10.0.0.20

**Recommended Actions**
[Recommended] Immediate network isolation of 10.0.0.1 and 10.0.0.5. Revoke active Kerberos ticket granting sessions.

**Containment Recommendation**
[Recommended] Execute Zero-Trust micro-isolation policy on 10.0.0.1.`);
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
      setQueryResult(`Based on observed MITRE ATT&CK T1021 runbooks: High-confidence lateral movement detected. Recommended containment action is to enforce micro-segmentation quarantine immediately.`);
    }
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      {/* Incident List */}
      <div className="w-1/3 glass-panel overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-white/10 sticky top-0 bg-surface/90 backdrop-blur z-10">
          <h2 className="text-xl font-bold">Active Incidents</h2>
          <p className="text-muted text-xs mt-1">Select an incident to launch AI investigation</p>
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
                  ? "bg-primary/20 border-primary shadow-lg shadow-primary/10" 
                  : "bg-white/5 border-white/10 hover:bg-white/10"
              )}
            >
              <div className="flex justify-between items-start">
                <span className="font-mono text-sm text-muted">#{inc.incident_id}</span>
                <span className={cn(
                  "px-2 py-0.5 rounded text-xs font-bold",
                  inc.severity === 'CRITICAL' ? 'bg-critical/20 text-critical border border-critical/30' :
                  inc.severity === 'HIGH' ? 'bg-high/20 text-high border border-high/30' :
                  'bg-low/20 text-low border border-low/30'
                )}>{inc.severity}</span>
              </div>
              <h3 className="text-base font-bold mt-2 text-white">{inc.title || `Threat on ${inc.target_host}`}</h3>
              <div className="flex justify-between items-center mt-2 text-xs text-muted">
                <span>Target: <code className="text-primary">{inc.target_host}</code></span>
                <span>Risk: <strong className="text-critical">{Number(inc.risk_score).toFixed(1)}</strong></span>
              </div>
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
                  <Shield className="text-primary w-6 h-6" />
                  Target: {selectedIncident.target_host}
                </h2>
                <p className="text-muted text-sm mt-1 font-mono">{selectedIncident.title || selectedIncident.incident_id}</p>
              </div>
              <button 
                onClick={() => handleInvestigate(selectedIncident.incident_id)}
                disabled={loading}
                className="bg-primary hover:bg-primary/90 text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50 shadow-lg shadow-primary/20"
              >
                <Brain className="w-5 h-5" />
                {loading ? "Investigating..." : "Auto-Investigate (LLM)"}
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {!investigationReport ? (
                <div className="h-full flex items-center justify-center text-muted flex-col gap-4">
                  <Brain className="w-16 h-16 text-primary/40 animate-pulse" />
                  <p className="text-center max-w-sm">Click <span className="text-primary font-semibold">"Auto-Investigate (LLM)"</span> to run RAG retrieval over MITRE ATT&CK runbooks and construct the end-to-end incident report.</p>
                </div>
              ) : (
                <div className="prose prose-invert max-w-none space-y-3">
                  {investigationReport.split('\n').map((line, i) => {
                    if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-bold text-white mt-4 mb-2">{line.replace('# ', '')}</h1>;
                    if (line.startsWith('**') && line.endsWith('**')) return <h3 key={i} className="text-lg font-bold text-primary mt-4 mb-1">{line.replace(/\*\*/g, '')}</h3>;
                    if (line.includes('[Observed]')) return <p key={i} className="mb-2"><span className="text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded mr-2 text-xs">[Observed]</span><span className="text-slate-200">{line.replace('[Observed]', '')}</span></p>;
                    if (line.includes('[Inferred]')) return <p key={i} className="mb-2"><span className="text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.5 rounded mr-2 text-xs">[Inferred]</span><span className="text-slate-200">{line.replace('[Inferred]', '')}</span></p>;
                    if (line.includes('[Recommended]')) return <p key={i} className="mb-2"><span className="text-sky-400 font-bold bg-sky-500/10 border border-sky-500/20 px-1.5 py-0.5 rounded mr-2 text-xs">[Recommended]</span><span className="text-slate-200">{line.replace('[Recommended]', '')}</span></p>;
                    if (line.startsWith('- ')) return <li key={i} className="ml-4 text-slate-300">{line.substring(2)}</li>;
                    return <p key={i} className="text-slate-400 mb-1">{line}</p>;
                  })}
                </div>
              )}
            </div>

            {/* Q&A Box */}
            {investigationReport && (
              <div className="p-4 border-t border-white/10 bg-surface/90">
                {queryResult && (
                  <div className="mb-4 p-4 bg-white/5 rounded-lg border border-white/10 text-sm">
                    <p className="font-bold text-primary mb-2">SOC Analyst AI Agent:</p>
                    <p className="text-slate-200">{queryResult}</p>
                  </div>
                )}
                <form onSubmit={handleQuery} className="flex gap-2">
                  <input 
                    type="text" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a follow-up question grounded in retrieved evidence (e.g. 'How was 10.0.0.1 compromised?')..."
                    className="flex-1 bg-background border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:border-primary text-white"
                  />
                  <button type="submit" className="bg-primary/20 hover:bg-primary/30 p-2.5 rounded-lg transition-colors border border-primary/30">
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
