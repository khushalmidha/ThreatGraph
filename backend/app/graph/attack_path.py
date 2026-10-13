"""
Attack Path Reconstruction Engine for ThreatGraph.

Algorithms:
1. Weighted Shortest Path: Dijkstra's algorithm (nx.dijkstra_path)
   Edge cost c(u, v) = 1.0 / (risk_weight + 1e-9), prioritizing high-confidence / high-risk paths.
2. Temporal Traversal: Monotonically non-decreasing timestamp verification along lateral movement hops.
3. Blast Radius: Multi-source Breadth-First Search (BFS) over directed graph.
4. Critical Asset Identification: Tarjan's bridge / articulation points on undirected projection.
5. Network Partitioning: Connected components (Disjoint Set Union / DSU).
"""

from typing import List, Dict, Any, Set, Optional, Tuple
import datetime
import networkx as nx


class AttackPathBuilder:
    """
    Constructs, queries, and reconstructs multi-hop attack propagation paths
    across simulated network topologies.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_topology(self, topology: Any):
        """
        Initialize the directed graph state from topology data.
        Edges contain risk weight (higher = more anomalous), timestamp, and flow metadata.
        """
        self.graph.clear()
        edges = topology.get("links", []) if isinstance(topology, dict) else (topology or [])
        for edge in edges:
            self.graph.add_edge(
                edge["source"],
                edge["target"],
                weight=float(edge.get("weight", 1.0)),
                timestamp=edge.get("timestamp"),
                edge_type=edge.get("edge_type", "FLOW"),
                protocol=edge.get("protocol", "TCP"),
                dst_port=edge.get("dst_port", 0),
            )

    def compute_shortest_path(self, source: str, target: str) -> List[str]:
        """
        Computes the highest-risk path from source to target using Dijkstra.
        Weight = 1.0 / (risk_weight + 1e-9).
        Returns [] if source or target not in graph, or if unreachable.
        """
        if source not in self.graph or target not in self.graph:
            return []
        if source == target:
            return [source]

        try:
            path = nx.dijkstra_path(
                self.graph,
                source,
                target,
                weight=lambda u, v, d: 1.0 / (max(0.0, float(d.get("weight", 1.0))) + 1e-9),
            )
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def compute_temporal_attack_path(
        self, source: str, target: str, strict_order: bool = True
    ) -> Dict[str, Any]:
        """
        Reconstructs a temporally valid lateral movement path from source to target.
        Ensures that consecutive hops follow non-decreasing timestamps (t_{i} <= t_{i+1}).
        Returns structured hop metadata including path nodes, timestamps, and total risk.
        """
        if source not in self.graph or target not in self.graph:
            return {
                "success": False,
                "path": [],
                "hops": [],
                "total_risk": 0.0,
                "reason": "Source or target not in graph",
            }

        if source == target:
            return {
                "success": True,
                "path": [source],
                "hops": [],
                "total_risk": 0.0,
                "reason": "Root node already target",
            }

        # Priority BFS searching for optimal temporal path
        # Queue stores: (current_node, path_nodes, hops_info, last_timestamp, cumulative_cost)
        queue: List[Tuple[str, List[str], List[Dict[str, Any]], Optional[str], float]] = [
            (source, [source], [], None, 0.0)
        ]
        visited_states: Set[Tuple[str, Optional[str]]] = set()
        best_path_record: Optional[Dict[str, Any]] = None
        min_cost = float("inf")

        while queue:
            # Sort by cumulative cost (Dijkstra-like search over temporal paths)
            queue.sort(key=lambda x: x[4])
            curr, path, hops, last_ts, cost = queue.pop(0)

            if curr == target:
                if cost < min_cost:
                    min_cost = cost
                    best_path_record = {
                        "success": True,
                        "path": path,
                        "hops": hops,
                        "total_risk": round(
                            sum(h["weight"] for h in hops) / max(1, len(hops)), 4
                        ),
                        "reason": "Path found",
                    }
                continue

            state_key = (curr, last_ts)
            if state_key in visited_states:
                continue
            visited_states.add(state_key)

            for neighbor in self.graph.successors(curr):
                # Prevent cycles in the active path
                if neighbor in path:
                    continue

                edge_data = self.graph[curr][neighbor]
                edge_ts = edge_data.get("timestamp")
                edge_weight = float(edge_data.get("weight", 1.0))
                hop_cost = 1.0 / (edge_weight + 1e-9)

                # Check temporal validity
                if strict_order and last_ts is not None and edge_ts is not None:
                    try:
                        t_last = (
                            datetime.datetime.fromisoformat(last_ts)
                            if isinstance(last_ts, str)
                            else last_ts
                        )
                        t_edge = (
                            datetime.datetime.fromisoformat(edge_ts)
                            if isinstance(edge_ts, str)
                            else edge_ts
                        )
                        if t_edge < t_last:
                            # Causal violation: hop happened before current infection hop
                            continue
                    except Exception:
                        pass

                hop_info = {
                    "from": curr,
                    "to": neighbor,
                    "timestamp": edge_ts,
                    "weight": edge_weight,
                    "protocol": edge_data.get("protocol", "TCP"),
                    "dst_port": edge_data.get("dst_port", 0),
                }

                queue.append(
                    (
                        neighbor,
                        path + [neighbor],
                        hops + [hop_info],
                        edge_ts or last_ts,
                        cost + hop_cost,
                    )
                )

        if best_path_record:
            return best_path_record

        # Fallback to standard Dijkstra if strict temporal ordering yielded no path
        fallback_path = self.compute_shortest_path(source, target)
        if fallback_path:
            hops = []
            for i in range(len(fallback_path) - 1):
                u, v = fallback_path[i], fallback_path[i + 1]
                ed = self.graph[u][v]
                hops.append(
                    {
                        "from": u,
                        "to": v,
                        "timestamp": ed.get("timestamp"),
                        "weight": float(ed.get("weight", 1.0)),
                        "protocol": ed.get("protocol", "TCP"),
                        "dst_port": ed.get("dst_port", 0),
                    }
                )
            return {
                "success": True,
                "path": fallback_path,
                "hops": hops,
                "total_risk": round(
                    sum(h["weight"] for h in hops) / max(1, len(hops)), 4
                ),
                "reason": "Fallback to static Dijkstra (non-strict temporal)",
            }

        return {
            "success": False,
            "path": [],
            "hops": [],
            "total_risk": 0.0,
            "reason": "No path exists between nodes",
        }

    def compute_blast_radius(self, sources: List[str]) -> Set[str]:
        """
        Multi-source Breadth-First Search (BFS) to compute the set of all
        hosts reachable downstream from compromised sources.
        """
        visited = set()
        queue = [s for s in sources if s in self.graph]

        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(
                    [succ for succ in self.graph.successors(node) if succ not in visited]
                )
        return visited

    def find_articulation_points(self) -> List[str]:
        """
        Identifies critical chokepoints / articulation points in the network
        using Tarjan's algorithm on the undirected topology projection.
        """
        if len(self.graph) < 3:
            return []
        undirected_g = self.graph.to_undirected()
        try:
            return list(nx.articulation_points(undirected_g))
        except Exception:
            return []

    def get_connected_components(self) -> List[Set[str]]:
        """
        Computes network partitions / connected components using Union-Find / DSU.
        """
        undirected_g = self.graph.to_undirected()
        return list(nx.connected_components(undirected_g))

    def generate_attack_path_record(
        self, incident_id: str, primary_host: str, all_hosts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive incident attack reconstruction record.
        """
        blast_radius = list(self.compute_blast_radius([primary_host]))
        critical_assets = [
            n for n in self.find_articulation_points() if n in blast_radius
        ]

        # Prioritize path to critical asset or deepest blast radius host
        likely_path_info = {"path": [primary_host], "hops": []}
        if len(blast_radius) > 1:
            targets = [a for a in critical_assets if a != primary_host]
            if not targets:
                targets = [h for h in blast_radius if h != primary_host]
            if targets:
                target = targets[-1]
                likely_path_info = self.compute_temporal_attack_path(primary_host, target)

        return {
            "incident_id": incident_id,
            "primary_host": primary_host,
            "blast_radius": blast_radius,
            "blast_radius_count": len(blast_radius),
            "critical_assets": critical_assets,
            "likely_path": likely_path_info.get("path", [primary_host]),
            "hop_details": likely_path_info.get("hops", []),
            "total_risk": likely_path_info.get("total_risk", 0.0),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
