from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime

try:
    from app.models import GraphEvent
except ImportError:
    from backend.app.models import GraphEvent

def get_host_destinations_in_window(db: Session, host_ip: str, window_start: datetime.datetime, window_end: datetime.datetime):
    """who did host X talk to in window W"""
    query = db.query(GraphEvent.node_b).filter(
        GraphEvent.node_a == host_ip,
        GraphEvent.timestamp >= window_start,
        GraphEvent.timestamp <= window_end
    ).distinct()
    return [row[0] for row in query.all()]

def get_destination_diversity_over_windows(db: Session, host_ip: str, window_size_sec: int, num_windows: int, end_time: datetime.datetime):
    """how has host X's destination-diversity changed over the last N windows"""
    diversity = []
    for i in range(num_windows):
        win_end = end_time - datetime.timedelta(seconds=window_size_sec * i)
        win_start = win_end - datetime.timedelta(seconds=window_size_sec)
        dsts = get_host_destinations_in_window(db, host_ip, win_start, win_end)
        diversity.append({
            "window_start": win_start.isoformat(),
            "window_end": win_end.isoformat(),
            "unique_destinations": len(dsts)
        })
    return diversity
    
def get_current_topology(db: Session, lookback_sec: int = 3600):
    """GET /network/topology implementation"""
    win_start = datetime.datetime.utcnow() - datetime.timedelta(seconds=lookback_sec)
    events = db.query(GraphEvent).filter(GraphEvent.timestamp >= win_start).all()
    
    # If no events in lookback window, retrieve the most recent 100 events
    if not events:
        events = db.query(GraphEvent).order_by(GraphEvent.timestamp.desc()).limit(100).all()
    
    nodes = set()
    links = []
    for e in events:
        nodes.add(e.node_a)
        nodes.add(e.node_b)
        links.append({
            "source": e.node_a,
            "target": e.node_b,
            "weight": e.edge_features.get("bytes", 1) if e.edge_features else 1,
            "risk_contribution": e.edge_features.get("risk", 0.1) if e.edge_features else 0.1,
            "edge_type": e.edge_type or "FLOW"
        })
        
    return {
        "nodes": [{"id": n, "val": 1} for n in nodes],
        "links": links
    }
