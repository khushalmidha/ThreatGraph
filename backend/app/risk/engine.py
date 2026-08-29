from typing import Dict, Any, List
from .config import get_severity_band
import datetime

class RiskEngine:
    def __init__(self):
        # Weights for different components
        self.weights = {
            "graph_threat": 0.4,
            "transformer_score": 0.3,
            "anomaly_score": 0.2,
            "historical_risk": 0.1
        }
    
    def calculate_risk(self, 
                       host_id: str,
                       graph_prob: float, 
                       transformer_prob: float, 
                       anomaly_score: float, 
                       historical_risk: float,
                       asset_criticality: float = 1.0) -> Dict[str, Any]:
        
        # Raw weighted score (0 to 1)
        raw_score = (
            graph_prob * self.weights["graph_threat"] +
            transformer_prob * self.weights["transformer_score"] +
            (min(anomaly_score, 10.0) / 10.0) * self.weights["anomaly_score"] + # Normalize anomaly assuming max ~10
            historical_risk * self.weights["historical_risk"]
        )
        
        # Apply asset criticality multiplier
        adjusted_score = min(raw_score * asset_criticality, 1.0)
        
        # Scale to 0-100
        final_score = adjusted_score * 100.0
        
        evidence = [
            {"source": "graph_threat", "value": graph_prob, "weight": self.weights["graph_threat"]},
            {"source": "transformer_score", "value": transformer_prob, "weight": self.weights["transformer_score"]},
            {"source": "anomaly_score", "value": anomaly_score, "weight": self.weights["anomaly_score"]},
            {"source": "historical_risk", "value": historical_risk, "weight": self.weights["historical_risk"]},
            {"source": "asset_criticality", "multiplier": asset_criticality}
        ]
        
        return {
            "host_id": host_id,
            "score": final_score,
            "severity_band": get_severity_band(final_score),
            "evidence": evidence,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
