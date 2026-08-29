import { useEffect, useState, useRef } from 'react';
import { api } from '../lib/api';
import ForceGraph2D from 'react-force-graph-2d';
import { Network } from 'lucide-react';

export default function NetworkGraphPage() {
  const [graphData, setGraphData] = useState<{nodes: any[], links: any[]}>({ nodes: [], links: [] });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Try to resize with the container
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
    // Fetch topology
    api.get('/graph/topology').then(res => {
      // transform to react-force-graph format
      const links = res.data.map((edge: any) => ({
        source: edge.source,
        target: edge.target,
        weight: edge.weight,
        risk_contribution: edge.risk_contribution
      }));

      // Extract unique nodes
      const nodeSet = new Set<string>();
      links.forEach((l: any) => {
        nodeSet.add(l.source);
        nodeSet.add(l.target);
      });
      
      const nodes = Array.from(nodeSet).map(id => ({ id, val: 1 }));
      setGraphData({ nodes, links });
    });
  }, []);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white flex items-center gap-3">
          <Network className="w-8 h-8 text-primary" />
          Live Network Topology
        </h2>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary" /> <span className="text-sm text-muted">Normal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-critical" /> <span className="text-sm text-muted">High Risk</span>
          </div>
        </div>
      </div>
      
      <div ref={containerRef} className="flex-1 glass-panel overflow-hidden border border-white/10 rounded-xl relative bg-[#0f172a]">
        {graphData.nodes.length > 0 ? (
          <ForceGraph2D
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            nodeLabel="id"
            nodeColor={(node: any) => {
              // Simple mock logic for coloring
              if (node.id === '10.0.0.10' || node.id === '10.0.0.2') return '#ef4444'; // critical
              return '#3b82f6'; // primary
            }}
            nodeRelSize={6}
            linkColor={() => 'rgba(255,255,255,0.2)'}
            linkWidth={(link: any) => Math.max(1, (link.weight || 1) * 2)}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={(d: any) => d.weight * 0.01}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-muted">
            Loading topology...
          </div>
        )}
      </div>
    </div>
  );
}
