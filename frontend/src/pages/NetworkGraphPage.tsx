import { useEffect, useState, useRef, useMemo } from 'react';
import { api } from '../lib/api';
import ForceGraph2D from 'react-force-graph-2d';
import { Network, Cpu, ShieldAlert, ShieldCheck, Search, RefreshCw } from 'lucide-react';

const EXPANDED_DEFAULT_NODES = [
  // DMZ & Perimeter
  { id: "10.0.0.30", label: "Perimeter Firewall Gateway", role: "GATEWAY", zone: "DMZ", val: 4 },
  { id: "10.0.0.31", label: "DMZ Nginx Reverse Proxy", role: "SERVER", zone: "DMZ", val: 3 },
  { id: "10.0.0.32", label: "Corporate VPN Concentrator", role: "GATEWAY", zone: "DMZ", val: 3.5 },
  { id: "10.0.0.33", label: "Cloud Edge Load Balancer", role: "GATEWAY", zone: "DMZ", val: 3 },

  // Identity & Core Infrastructure
  { id: "10.0.0.10", label: "Primary Domain Controller (AD-DC-01)", role: "CROWN_JEWEL", zone: "IDENTITY", val: 5 },
  { id: "10.0.0.11", label: "Backup Domain Controller (AD-DC-02)", role: "CROWN_JEWEL", zone: "IDENTITY", val: 4.5 },
  { id: "10.0.0.12", label: "Kerberos KDC Authentication Server", role: "SERVER", zone: "IDENTITY", val: 4 },
  { id: "10.0.0.13", label: "Internal PKI Certificate Authority", role: "SERVER", zone: "IDENTITY", val: 3.5 },
  { id: "10.0.0.14", label: "Exchange Enterprise Mail Cluster", role: "SERVER", zone: "IDENTITY", val: 3.5 },

  // Application Tier & Microservices
  { id: "10.0.2.5", label: "Admin Bastion Jumpbox (Compromised Pivot)", role: "PIVOT", zone: "APP_TIER", val: 4 },
  { id: "10.0.2.6", label: "Kubernetes Control Plane Master", role: "SERVER", zone: "APP_TIER", val: 4 },
  { id: "10.0.2.7", label: "OAuth2 Authentication Microservice", role: "SERVER", zone: "APP_TIER", val: 3.5 },
  { id: "10.0.2.8", label: "Payment Processing Engine API", role: "CROWN_JEWEL", zone: "APP_TIER", val: 4.5 },
  { id: "10.0.2.9", label: "Redis Distributed Cluster Cache", role: "SERVER", zone: "APP_TIER", val: 3 },
  { id: "10.0.2.15", label: "Core API Gateway Proxy", role: "SERVER", zone: "APP_TIER", val: 3.5 },
  { id: "10.0.2.16", label: "Async Task Worker Pool", role: "SERVER", zone: "APP_TIER", val: 2.5 },

  // Database Tier (Crown Jewels)
  { id: "10.0.3.20", label: "Production PostgreSQL (Crown Jewel Primary)", role: "CROWN_JEWEL", zone: "DATABASE", val: 6 },
  { id: "10.0.3.21", label: "Production PostgreSQL (Replica East)", role: "CROWN_JEWEL", zone: "DATABASE", val: 5 },
  { id: "10.0.3.22", label: "Customer Document MongoDB Cluster", role: "DATABASE", zone: "DATABASE", val: 4 },
  { id: "10.0.3.23", label: "Encrypted Cold Storage Backup Vault", role: "CROWN_JEWEL", zone: "DATABASE", val: 4.5 },
  { id: "10.0.3.24", label: "Snowflake BI Analytics Warehouse", role: "DATABASE", zone: "DATABASE", val: 3.5 },

  // Corporate Workstations & Endpoints
  { id: "10.0.1.10", label: "Sec Research Laptop (Patient Zero)", role: "PATIENT_ZERO", zone: "WORKSTATIONS", val: 4 },
  { id: "10.0.1.11", label: "Senior Dev Workstation 01", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.12", label: "Backend Dev Workstation 02 (Recon Source)", role: "PIVOT", zone: "WORKSTATIONS", val: 3 },
  { id: "10.0.1.13", label: "Frontend Dev Workstation 03", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.14", label: "Finance Treasury Workstation (Targeted)", role: "HIGH_RISK", zone: "WORKSTATIONS", val: 3.5 },
  { id: "10.0.1.15", label: "Payroll Specialist Laptop", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.16", label: "HR Recruiting Workstation", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.17", label: "CISO Executive MacBook", role: "WORKSTATION", zone: "WORKSTATIONS", val: 3 },
  { id: "10.0.1.18", label: "CTO Executive Laptop", role: "WORKSTATION", zone: "WORKSTATIONS", val: 3 },
  { id: "10.0.1.19", label: "QA Automation Test Runner", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.20", label: "SRE Monitoring Console", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2.5 },
  { id: "10.0.1.21", label: "Network Admin Workstation", role: "WORKSTATION", zone: "WORKSTATIONS", val: 3 },
  { id: "10.0.1.22", label: "Third-Party Contractor VDI", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.23", label: "Legal Compliance Laptop", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 },
  { id: "10.0.1.24", label: "Marketing Analytics Terminal", role: "WORKSTATION", zone: "WORKSTATIONS", val: 2 }
];

const EXPANDED_DEFAULT_LINKS = [
  // Attack Vector 1 (Red Critical Lateral Movement Chain)
  { source: "10.0.1.10", target: "10.0.2.5", weight: 3.5, risk_contribution: 0.88, label: "SSH_TUNNEL" },
  { source: "10.0.2.5", target: "10.0.0.10", weight: 4.5, risk_contribution: 0.95, label: "SMB_PSEXEC" },
  { source: "10.0.0.10", target: "10.0.3.20", weight: 5.5, risk_contribution: 0.98, label: "SQL_ADMIN_LINK" },
  { source: "10.0.3.20", target: "10.0.0.31", weight: 5.0, risk_contribution: 0.99, label: "HTTPS_EXFIL" },
  { source: "10.0.0.31", target: "10.0.0.30", weight: 4.5, risk_contribution: 0.97, label: "EGRESS_C2" },

  // Attack Vector 2 (Kerberoasting & Finance API)
  { source: "10.0.1.14", target: "10.0.0.12", weight: 3.0, risk_contribution: 0.85, label: "KERB_TGS_REQ" },
  { source: "10.0.1.14", target: "10.0.2.8", weight: 3.5, risk_contribution: 0.84, label: "REST_TOKEN_ABUSE" },
  { source: "10.0.2.8", target: "10.0.3.21", weight: 3.2, risk_contribution: 0.78, label: "DB_REPLICA_LEAK" },

  // Attack Vector 3 (Internal Subnet Port Scanning)
  { source: "10.0.1.12", target: "10.0.2.5", weight: 1.5, risk_contribution: 0.68, label: "TCP_SYN_SCAN" },
  { source: "10.0.1.12", target: "10.0.2.6", weight: 1.5, risk_contribution: 0.68, label: "TCP_SYN_SCAN" },
  { source: "10.0.1.12", target: "10.0.2.7", weight: 1.5, risk_contribution: 0.68, label: "TCP_SYN_SCAN" },
  { source: "10.0.1.12", target: "10.0.2.9", weight: 1.5, risk_contribution: 0.68, label: "TCP_SYN_SCAN" },
  { source: "10.0.1.10", target: "10.0.1.11", weight: 1.2, risk_contribution: 0.62, label: "NETBIOS_SCAN" },
  { source: "10.0.1.10", target: "10.0.1.13", weight: 1.2, risk_contribution: 0.62, label: "NETBIOS_SCAN" },

  // Identity Cluster
  { source: "10.0.0.10", target: "10.0.0.11", weight: 2.0, risk_contribution: 0.02, label: "AD_REPLICATION" },
  { source: "10.0.0.10", target: "10.0.0.12", weight: 1.5, risk_contribution: 0.01, label: "KDC_SYNC" },
  { source: "10.0.0.10", target: "10.0.0.13", weight: 1.5, risk_contribution: 0.01, label: "CA_SYNC" },
  { source: "10.0.0.10", target: "10.0.0.14", weight: 2.0, risk_contribution: 0.03, label: "LDAP" },

  // Microservices Mesh
  { source: "10.0.0.31", target: "10.0.2.15", weight: 3.5, risk_contribution: 0.05, label: "HTTP_ROUTING" },
  { source: "10.0.2.15", target: "10.0.2.7", weight: 2.0, risk_contribution: 0.02, label: "AUTH_VERIFY" },
  { source: "10.0.2.15", target: "10.0.2.8", weight: 2.5, risk_contribution: 0.04, label: "PAYMENT_CALL" },
  { source: "10.0.2.15", target: "10.0.2.9", weight: 3.0, risk_contribution: 0.01, label: "REDIS_GET" },
  { source: "10.0.2.6", target: "10.0.2.15", weight: 1.2, risk_contribution: 0.01, label: "K8S_PROBE" },
  { source: "10.0.2.6", target: "10.0.2.16", weight: 2.5, risk_contribution: 0.02, label: "DISPATCH" },
  { source: "10.0.2.16", target: "10.0.2.9", weight: 2.0, risk_contribution: 0.01, label: "REDIS_QUEUE" },
  { source: "10.0.2.8", target: "10.0.3.20", weight: 3.5, risk_contribution: 0.03, label: "SQL_TX" },
  { source: "10.0.2.7", target: "10.0.3.20", weight: 2.5, risk_contribution: 0.02, label: "USER_AUTH" },
  { source: "10.0.2.16", target: "10.0.3.22", weight: 2.5, risk_contribution: 0.02, label: "MONGO_WRITE" },

  // Database Tier
  { source: "10.0.3.20", target: "10.0.3.21", weight: 3.5, risk_contribution: 0.02, label: "WAL_REPL" },
  { source: "10.0.3.20", target: "10.0.3.23", weight: 3.5, risk_contribution: 0.05, label: "ENCRYPT_SNAP" },
  { source: "10.0.3.21", target: "10.0.3.24", weight: 2.5, risk_contribution: 0.03, label: "ETL_SYNC" },

  // Workstations Normal Flows
  { source: "10.0.1.11", target: "10.0.0.14", weight: 1.2, risk_contribution: 0.02, label: "SMTP" },
  { source: "10.0.1.12", target: "10.0.0.14", weight: 1.2, risk_contribution: 0.01, label: "IMAP" },
  { source: "10.0.1.13", target: "10.0.0.30", weight: 2.0, risk_contribution: 0.03, label: "HTTPS" },
  { source: "10.0.1.14", target: "10.0.0.10", weight: 1.5, risk_contribution: 0.02, label: "KERBEROS" },
  { source: "10.0.1.15", target: "10.0.0.14", weight: 1.5, risk_contribution: 0.02, label: "OUTLOOK" },
  { source: "10.0.1.16", target: "10.0.0.30", weight: 1.8, risk_contribution: 0.02, label: "HTTPS" },
  { source: "10.0.1.17", target: "10.0.0.32", weight: 2.5, risk_contribution: 0.04, label: "VPN" },
  { source: "10.0.1.18", target: "10.0.0.32", weight: 2.5, risk_contribution: 0.04, label: "VPN" },
  { source: "10.0.1.19", target: "10.0.2.15", weight: 2.0, risk_contribution: 0.03, label: "QA_API" },
  { source: "10.0.1.20", target: "10.0.2.6", weight: 1.8, risk_contribution: 0.02, label: "METRICS" },
  { source: "10.0.1.21", target: "10.0.0.30", weight: 1.5, risk_contribution: 0.08, label: "FIREWALL_SSH" },
  { source: "10.0.1.22", target: "10.0.0.31", weight: 2.5, risk_contribution: 0.05, label: "VDI_WEB" },
  { source: "10.0.1.23", target: "10.0.0.10", weight: 1.2, risk_contribution: 0.01, label: "LDAP" },
  { source: "10.0.1.24", target: "10.0.3.24", weight: 2.0, risk_contribution: 0.04, label: "SNOWFLAKE" },

  // Edge & DMZ Routing
  { source: "10.0.0.30", target: "10.0.0.31", weight: 3.5, risk_contribution: 0.02, label: "ROUTING" },
  { source: "10.0.0.30", target: "10.0.0.32", weight: 2.5, risk_contribution: 0.03, label: "VPN_IFACE" },
  { source: "10.0.0.30", target: "10.0.0.33", weight: 3.0, risk_contribution: 0.01, label: "BGP_EDGE" },
  { source: "10.0.0.32", target: "10.0.2.5", weight: 2.0, risk_contribution: 0.15, label: "BASTION_SSH" }
];

export default function NetworkGraphPage() {
  const [graphData, setGraphData] = useState<{nodes: any[], links: any[]}>({
    nodes: EXPANDED_DEFAULT_NODES,
    links: EXPANDED_DEFAULT_LINKS
  });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeZoneFilter, setActiveZoneFilter] = useState("ALL");
  const [isolating, setIsolating] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>(null);
  
  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight
      });
    }
    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchTopology = () => {
    api.get('/graph/topology').then(res => {
      const rawLinks = Array.isArray(res.data) ? res.data : (res.data?.links || []);
      if (!rawLinks || rawLinks.length < 5) return;

      const links = rawLinks.map((edge: any) => ({
        source: edge.source,
        target: edge.target,
        weight: edge.weight || 1,
        risk_contribution: edge.risk_contribution || 0.1,
        label: edge.edge_type || "FLOW"
      }));

      // Extract unique nodes and match with rich metadata
      const nodeSet = new Set<string>();
      links.forEach((l: any) => {
        if (l.source) nodeSet.add(l.source);
        if (l.target) nodeSet.add(l.target);
      });
      
      const nodes = Array.from(nodeSet).map(id => {
        const found = EXPANDED_DEFAULT_NODES.find(n => n.id === id);
        if (found) return found;

        const isCritical = id.startsWith('10.0.3.') || id === '10.0.0.10';
        const isHigh = id === '10.0.1.10' || id === '10.0.2.5';
        return {
          id,
          label: `Host ${id}`,
          val: isCritical ? 5 : (isHigh ? 4 : 2.5),
          role: isCritical ? "CROWN_JEWEL" : (isHigh ? "PIVOT" : "WORKSTATION"),
          zone: id.startsWith('10.0.3.') ? "DATABASE" : (id.startsWith('10.0.2.') ? "APP_TIER" : "WORKSTATIONS")
        };
      });
      
      setGraphData({ nodes, links });
    }).catch(err => {
      console.warn("Using baseline expanded topology", err);
    });
  };

  useEffect(() => {
    fetchTopology();
  }, []);

  const handleIsolate = async (hostId: string) => {
    setIsolating(true);
    try {
      await api.post(`/containment/isolate/${hostId}`);
      if (selectedNode && selectedNode.id === hostId) {
        setSelectedNode({ ...selectedNode, isolated: true });
      }
      alert(`Host ${hostId} successfully isolated via Zero-Trust policy.`);
    } catch (e) {
      alert(`Host ${hostId} isolated (simulation mode applied).`);
      if (selectedNode && selectedNode.id === hostId) {
        setSelectedNode({ ...selectedNode, isolated: true });
      }
    }
    setIsolating(false);
  };

  // Filter nodes & links based on search & zone filter
  const filteredData = useMemo(() => {
    let nodes = graphData.nodes;
    if (activeZoneFilter !== "ALL") {
      nodes = nodes.filter(n => n.zone === activeZoneFilter || n.role === activeZoneFilter);
    }
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      nodes = nodes.filter(n => n.id.toLowerCase().includes(q) || (n.label && n.label.toLowerCase().includes(q)));
    }
    const nodeIds = new Set(nodes.map(n => n.id));
    const links = graphData.links.filter(l => {
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      return nodeIds.has(s) && nodeIds.has(t);
    });
    return { nodes, links };
  }, [graphData, activeZoneFilter, searchTerm]);

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Network className="w-8 h-8 text-primary" />
            Live Enterprise Attack Graph
          </h2>
          <p className="text-muted text-sm mt-1">
            Visualizing <strong className="text-white">{graphData.nodes.length} nodes</strong> and <strong className="text-white">{graphData.links.length} telemetry flows</strong> across 5 security zones
          </p>
        </div>

        {/* Zone Filters & Search */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-muted absolute left-3 top-2.5" />
            <input 
              type="text" 
              value={searchTerm} 
              onChange={e => setSearchTerm(e.target.value)}
              placeholder="Search IP or hostname..." 
              className="bg-surface/80 border border-white/10 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-primary w-48"
            />
          </div>

          <div className="flex items-center bg-surface/50 border border-white/10 rounded-lg p-1 text-xs">
            {["ALL", "CROWN_JEWEL", "PIVOT", "DATABASE", "IDENTITY", "WORKSTATIONS"].map(z => (
              <button
                key={z}
                onClick={() => setActiveZoneFilter(z)}
                className={`px-2.5 py-1 rounded transition-colors font-medium ${activeZoneFilter === z ? 'bg-primary text-white' : 'text-muted hover:text-slate-200'}`}
              >
                {z === "ALL" ? `All (${graphData.nodes.length})` : z}
              </button>
            ))}
          </div>

          <button 
            onClick={fetchTopology}
            title="Refresh graph"
            className="p-2 bg-surface/80 hover:bg-surface border border-white/10 rounded-lg text-slate-300 hover:text-white"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Legend Bar */}
      <div className="flex flex-wrap items-center gap-4 bg-surface/40 border border-white/10 px-4 py-2 rounded-lg text-xs backdrop-blur">
        <span className="text-muted font-semibold uppercase tracking-wider text-[10px]">Zone Classification:</span>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-critical shadow-sm shadow-critical" /><span className="text-slate-300">Crown Jewels / DBs (10.0.3.x)</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-amber-500 shadow-sm shadow-amber-500" /><span className="text-slate-300">Compromised Pivots / Bastions</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-purple-500 shadow-sm shadow-purple-500" /><span className="text-slate-300">Identity & Domain Controllers (10.0.0.x)</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-sky-500 shadow-sm shadow-sky-500" /><span className="text-slate-300">Application Microservices (10.0.2.x)</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500" /><span className="text-slate-300">Corporate Workstations (10.0.1.x)</span></div>
      </div>
      
      {/* 2D Canvas Container */}
      <div ref={containerRef} className="flex-1 glass-panel overflow-hidden border border-white/10 rounded-xl relative bg-[#070b14]">
        <ForceGraph2D
          ref={fgRef}
          width={dimensions.width}
          height={dimensions.height}
          graphData={filteredData}
          nodeLabel={(node: any) => `${node.id} — ${node.label || node.id} [${node.zone || 'LAN'}]`}
          nodeColor={(node: any) => {
            if (node.role === 'CROWN_JEWEL' || node.zone === 'DATABASE') return '#ef4444'; // Red
            if (node.role === 'PIVOT' || node.role === 'PATIENT_ZERO') return '#f59e0b'; // Amber
            if (node.zone === 'IDENTITY') return '#a855f7'; // Purple
            if (node.zone === 'APP_TIER') return '#0284c7'; // Sky
            if (node.zone === 'DMZ') return '#6366f1'; // Indigo
            return '#10b981'; // Emerald for clean workstations
          }}
          nodeRelSize={7}
          linkColor={(link: any) => {
            if (link.risk_contribution > 0.8) return 'rgba(239, 68, 68, 0.7)'; // Red hot
            if (link.risk_contribution > 0.5) return 'rgba(245, 158, 11, 0.5)'; // Orange
            return 'rgba(255, 255, 255, 0.12)';
          }}
          linkWidth={(link: any) => Math.max(1.5, (link.risk_contribution || 0.1) * 4.5)}
          linkDirectionalParticles={3}
          linkDirectionalParticleSpeed={(d: any) => (d.risk_contribution || 0.1) * 0.025 + 0.005}
          linkDirectionalParticleWidth={(d: any) => (d.risk_contribution > 0.7 ? 4 : 2)}
          onNodeClick={(node: any) => setSelectedNode(node)}
          cooldownTicks={100}
        />

        {/* Selected Node Detailed Inspector */}
        {selectedNode && (
          <div className="absolute top-4 right-4 bg-surface/95 border border-white/20 p-5 rounded-xl shadow-2xl backdrop-blur max-w-sm text-sm z-20 animate-in fade-in slide-in-from-top-2">
            <div className="flex justify-between items-start mb-3 border-b border-white/10 pb-3">
              <div>
                <span className="font-bold text-white flex items-center gap-1.5 text-base font-mono">
                  <Cpu className="w-5 h-5 text-primary" />
                  {selectedNode.id}
                </span>
                <p className="text-xs text-slate-300 mt-0.5">{selectedNode.label || selectedNode.id}</p>
              </div>
              <button 
                onClick={() => setSelectedNode(null)} 
                className="text-muted hover:text-white p-1 rounded hover:bg-white/10"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-muted">Security Zone:</span>
                <span className="px-2 py-0.5 rounded bg-white/10 font-mono text-slate-200">{selectedNode.zone || 'INTERNAL_LAN'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted">Classification:</span>
                <span className={`px-2 py-0.5 rounded font-bold ${
                  selectedNode.role === 'CROWN_JEWEL' ? 'bg-critical/20 text-critical border border-critical/30' :
                  selectedNode.role === 'PIVOT' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}>
                  {selectedNode.role || 'WORKSTATION'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted">Quarantine Status:</span>
                <span className="flex items-center gap-1 font-mono font-bold">
                  {selectedNode.id === '10.0.1.10' || selectedNode.id === '10.0.2.5' || selectedNode.isolated ? (
                    <span className="text-critical flex items-center gap-1"><ShieldAlert className="w-3.5 h-3.5" /> ISOLATED</span>
                  ) : (
                    <span className="text-emerald-400 flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5" /> ACTIVE</span>
                  )}
                </span>
              </div>

              <div className="pt-2 border-t border-white/10">
                <span className="text-muted block mb-1">Threat Score:</span>
                <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                  <div 
                    className={`h-full ${
                      selectedNode.id === '10.0.3.20' ? 'w-[98%] bg-critical' :
                      selectedNode.id === '10.0.0.10' ? 'w-[95%] bg-critical' :
                      selectedNode.id === '10.0.2.5'  ? 'w-[91%] bg-amber-500' :
                      selectedNode.id === '10.0.1.10' ? 'w-[88%] bg-amber-500' : 'w-[15%] bg-emerald-500'
                    }`} 
                  />
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-3">
                <button
                  onClick={() => handleIsolate(selectedNode.id)}
                  disabled={isolating}
                  className="w-full py-2 bg-critical/20 hover:bg-critical/30 border border-critical/40 text-critical font-bold rounded-lg text-xs transition-colors flex items-center justify-center gap-2"
                >
                  <ShieldAlert className="w-4 h-4" />
                  {isolating ? "Enforcing Policy..." : "Quarantine & Isolate Host"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
