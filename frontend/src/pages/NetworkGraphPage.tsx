import { useEffect, useState, useRef } from 'react';
import { api } from '../lib/api';
import ForceGraph2D from 'react-force-graph-2d';
import { Network, Cpu } from 'lucide-react';

const DEFAULT_GRAPH = {
  nodes: [
    { id: "10.0.0.1", label: "Patient Zero (Workstation-01)", role: "PATIENT_ZERO", val: 3 },
    { id: "10.0.0.2", label: "Workstation-02 (Finance)", role: "WORKSTATION", val: 2 },
    { id: "10.0.0.3", label: "Workstation-03 (Dev)", role: "WORKSTATION", val: 2 },
    { id: "10.0.0.4", label: "Laptop-04 (HR)", role: "WORKSTATION", val: 2 },
    { id: "10.0.0.5", label: "Jump Box Pivot Server", role: "PIVOT", val: 3.5 },
    { id: "10.0.0.10", label: "Domain Controller (AD-DC-01)", role: "CROWN_JEWEL", val: 4.5 },
    { id: "10.0.0.11", label: "Exchange Mail Server", role: "SERVER", val: 3 },
    { id: "10.0.0.20", label: "Production DB Cluster (Crown Jewel)", role: "CROWN_JEWEL", val: 5 },
    { id: "10.0.0.30", label: "Core Security Gateway", role: "GATEWAY", val: 3.5 }
  ],
  links: [
    { source: "10.0.0.1", target: "10.0.0.5", weight: 3, risk_contribution: 0.85, label: "SSH Pivot Tunnel" },
    { source: "10.0.0.5", target: "10.0.0.10", weight: 4.5, risk_contribution: 0.94, label: "SMB PsExec & DCSync" },
    { source: "10.0.0.10", target: "10.0.0.20", weight: 5, risk_contribution: 0.98, label: "TDS Exfiltration Attempt" },
    { source: "10.0.0.1", target: "10.0.0.2", weight: 1.5, risk_contribution: 0.65, label: "NetBIOS Scan" },
    { source: "10.0.0.2", target: "10.0.0.11", weight: 1.2, risk_contribution: 0.05, label: "SMTP" },
    { source: "10.0.0.3", target: "10.0.0.11", weight: 1.2, risk_contribution: 0.05, label: "IMAP" },
    { source: "10.0.0.4", target: "10.0.0.30", weight: 1.5, risk_contribution: 0.04, label: "HTTPS" },
    { source: "10.0.0.11", target: "10.0.0.30", weight: 2, risk_contribution: 0.08, label: "Relay" },
    { source: "10.0.0.5", target: "10.0.0.30", weight: 2.5, risk_contribution: 0.20, label: "VPN" },
    { source: "10.0.0.20", target: "10.0.0.30", weight: 3, risk_contribution: 0.35, label: "Backup" }
  ]
};

export default function NetworkGraphPage() {
  const [graphData, setGraphData] = useState<{nodes: any[], links: any[]}>(DEFAULT_GRAPH);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
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

  useEffect(() => {
    // Fetch topology from backend
    api.get('/graph/topology').then(res => {
      const rawLinks = Array.isArray(res.data) ? res.data : (res.data?.links || []);
      if (!rawLinks || rawLinks.length === 0) return;

      const links = rawLinks.map((edge: any) => ({
        source: edge.source,
        target: edge.target,
        weight: edge.weight || 1,
        risk_contribution: edge.risk_contribution || 0.1,
        label: edge.edge_type || "FLOW"
      }));

      // Extract unique nodes
      const nodeSet = new Set<string>();
      links.forEach((l: any) => {
        if (l.source) nodeSet.add(l.source);
        if (l.target) nodeSet.add(l.target);
      });
      
      const nodes = Array.from(nodeSet).map(id => {
        const isCritical = id === '10.0.0.10' || id === '10.0.0.20';
        const isHigh = id === '10.0.0.1' || id === '10.0.0.5';
        return {
          id,
          label: id,
          val: isCritical ? 4.5 : (isHigh ? 3 : 2),
          role: isCritical ? "CROWN_JEWEL" : (isHigh ? "PIVOT" : "WORKSTATION")
        };
      });
      
      setGraphData({ nodes, links });
    }).catch(err => {
      console.warn("Using baseline topology", err);
    });
  }, []);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Network className="w-8 h-8 text-primary" />
            Live Attack Graph Topology
          </h2>
          <p className="text-muted text-sm mt-1">Multi-hop graph neural network propagation path & blast radius visualization</p>
        </div>
        <div className="flex gap-4 bg-surface/50 border border-white/10 px-4 py-2 rounded-lg backdrop-blur">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-critical shadow-sm shadow-critical" />
            <span className="text-xs text-muted">Crown Jewel / Target</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-500 shadow-sm shadow-amber-500" />
            <span className="text-xs text-muted">Compromised Pivot</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary shadow-sm shadow-primary" />
            <span className="text-xs text-muted">Enterprise Workstation</span>
          </div>
        </div>
      </div>
      
      <div ref={containerRef} className="flex-1 glass-panel overflow-hidden border border-white/10 rounded-xl relative bg-[#090d16]">
        <ForceGraph2D
          width={dimensions.width}
          height={dimensions.height}
          graphData={graphData}
          nodeLabel={(node: any) => `${node.id} (${node.label || node.id})`}
          nodeColor={(node: any) => {
            if (node.id === '10.0.0.10' || node.id === '10.0.0.20' || node.role === 'CROWN_JEWEL') return '#ef4444';
            if (node.id === '10.0.0.1' || node.id === '10.0.0.5' || node.role === 'PIVOT') return '#f59e0b';
            if (node.id === '10.0.0.30' || node.role === 'GATEWAY') return '#8b5cf6';
            return '#3b82f6';
          }}
          nodeRelSize={6}
          linkColor={(link: any) => {
            if (link.risk_contribution > 0.8) return 'rgba(239, 68, 68, 0.6)';
            if (link.risk_contribution > 0.4) return 'rgba(245, 158, 11, 0.4)';
            return 'rgba(255, 255, 255, 0.15)';
          }}
          linkWidth={(link: any) => Math.max(1.5, (link.risk_contribution || 0.2) * 4)}
          linkDirectionalParticles={3}
          linkDirectionalParticleSpeed={(d: any) => (d.risk_contribution || 0.2) * 0.02 + 0.005}
          linkDirectionalParticleWidth={(d: any) => (d.risk_contribution > 0.7 ? 4 : 2)}
          onNodeClick={(node: any) => setSelectedNode(node)}
        />

        {selectedNode && (
          <div className="absolute top-4 right-4 bg-surface/95 border border-white/20 p-4 rounded-xl shadow-2xl backdrop-blur max-w-xs text-sm">
            <div className="flex justify-between items-center mb-2">
              <span className="font-bold text-white flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-primary" />
                {selectedNode.id}
              </span>
              <button onClick={() => setSelectedNode(null)} className="text-muted hover:text-white">✕</button>
            </div>
            <p className="text-xs text-slate-300 font-mono mb-2">{selectedNode.label || selectedNode.id}</p>
            <div className="text-xs space-y-1 text-slate-400">
              <div>Role: <span className="text-white font-mono">{selectedNode.role || 'HOST'}</span></div>
              <div>Status: <span className={selectedNode.id === '10.0.0.1' ? 'text-critical font-bold' : 'text-emerald-400'}>
                {selectedNode.id === '10.0.0.1' ? 'ISOLATED' : 'ACTIVE'}
              </span></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
