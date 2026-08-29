import sys
import os
import pytest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.app.graph.queries import get_current_topology, get_host_destinations_in_window
from backend.app.models import GraphEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_topology_query(db_session):
    now = datetime.utcnow()
    # Add mock data
    e1 = GraphEvent(
        event_id="1", timestamp=now, node_a="10.0.0.1", node_b="10.0.0.2", 
        edge_type="communication", edge_features={"bytes": 500}
    )
    e2 = GraphEvent(
        event_id="2", timestamp=now - timedelta(seconds=100), node_a="10.0.0.1", node_b="10.0.0.3", 
        edge_type="communication", edge_features={"bytes": 1000}
    )
    db_session.add_all([e1, e2])
    db_session.commit()
    
    topology = get_current_topology(db_session, lookback_sec=300)
    assert len(topology["nodes"]) == 3
    assert len(topology["links"]) == 2
    
    topology_short = get_current_topology(db_session, lookback_sec=50)
    assert len(topology_short["nodes"]) == 2
    assert len(topology_short["links"]) == 1
