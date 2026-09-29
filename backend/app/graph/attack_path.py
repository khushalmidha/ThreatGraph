from typing import List, Dict, Any, Set
import networkx as nx
from collections import defaultdict
import datetime
import uuid

class AttackPathBuilder:
    def __init__(self):
        # We use networkx for the algorithmic implementations
        self.graph = nx.DiGraph()
        
    def build_from_topology(self, topology: Any):
        """Initialize the graph state from current topology."""
        self.graph.clear()
        edges = topology.get("links", []) if isinstance(topology, dict) else (topology or [])
        for edge in edges:
            self.graph.add_edge(
                edge["source"], 
                edge["target"], 
                weight=edge.get("weight", 1.0),
                timestamp=edge.get("timestamp")
            )
            
    def compute_shortest_path(self, source: str, target: str) -> List[str]:
        """Weighted shortest path (Dijkstra). Weight = inverse of (confidence * risk)."""
        # Invert weights for shortest path where higher risk -> lower weight
        # Assumes weights in graph are already risk values
        try:
            path = nx.dijkstra_path(
                self.graph, 
                source, 
                target, 
                weight=lambda u, v, d: 1.0 / (d.get('weight', 1.0) + 1e-9)
            )
            return path
        except nx.NetworkXNoPath:
            return []
        
    def compute_blast_radius(self, sources: List[str]) -> Set[str]:
        """Multi-source BFS to compute blast radius."""
        visited = set()
        queue = sources.copy()
        
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                if node in self.graph:
                    queue.extend(list(self.graph.successors(node)))
        return visited

    def find_articulation_points(self) -> List[str]:
        """Tarjan's algorithm for articulation points (critical assets)."""
        # NetworkX articulation_points requires an undirected graph
        undirected_g = self.graph.to_undirected()
        try:
            return list(nx.articulation_points(undirected_g))
        except Exception:
            return []
            
    def get_connected_components(self) -> List[Set[str]]:
        """Union-Find (DSU) internally via networkx connected components."""
        undirected_g = self.graph.to_undirected()
        return list(nx.connected_components(undirected_g))
        
    def generate_attack_path_record(self, incident_id: str, primary_host: str, all_hosts: List[str]) -> Dict[str, Any]:
        """Generate a structured response for the attack path."""
        blast_radius = list(self.compute_blast_radius([primary_host]))
        critical_assets = [n for n in self.find_articulation_points() if n in blast_radius]
        
        # Build path to a random high-value asset in blast radius for demo
        path = []
        if len(blast_radius) > 1:
            target = blast_radius[-1] if blast_radius[-1] != primary_host else blast_radius[0]
            path = self.compute_shortest_path(primary_host, target)
            
        return {
            "incident_id": incident_id,
            "primary_host": primary_host,
            "blast_radius": blast_radius,
            "critical_assets": critical_assets,
            "likely_path": path,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
