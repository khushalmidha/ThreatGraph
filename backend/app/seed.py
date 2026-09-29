import datetime
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models

def seed_database(db: Session = None):
    close_at_end = False
    if db is None:
        db = SessionLocal()
        close_at_end = True
        
    try:
        # Create all tables if not exists
        models.Base.metadata.create_all(bind=engine)
        
        # Check if already seeded
        existing_incidents = db.query(models.Incident).count()
        if existing_incidents > 0:
            print("[Seed] Database already contains incidents. Skipping duplicate seed.")
            return {"status": "already_seeded", "incidents": existing_incidents}

        print("[Seed] Populating rich enterprise dummy data...")
        now = datetime.datetime.utcnow()
        
        # 1. Hosts
        hosts_data = [
            ("HOST-WS-01", "10.0.0.1", "eng-workstation-01", "WORKSTATION", "MEDIUM"),
            ("HOST-WS-02", "10.0.0.2", "fin-workstation-02", "WORKSTATION", "MEDIUM"),
            ("HOST-WS-03", "10.0.0.3", "dev-workstation-03", "WORKSTATION", "LOW"),
            ("HOST-WS-04", "10.0.0.4", "hr-laptop-04", "LAPTOP", "LOW"),
            ("HOST-SRV-JB", "10.0.0.5", "jump-box-internal", "SERVER", "HIGH"),
            ("HOST-SRV-DC", "10.0.0.10", "ad-domain-controller-01", "DOMAIN_CONTROLLER", "CRITICAL"),
            ("HOST-SRV-MAIL", "10.0.0.11", "exchange-mail-cluster", "SERVER", "HIGH"),
            ("HOST-DB-PROD", "10.0.0.20", "prod-db-cluster-01", "DATABASE", "CRITICAL"),
            ("HOST-GW-01", "10.0.0.30", "core-router-gateway", "GATEWAY", "HIGH"),
        ]
        
        for h_id, ip, name, h_type, crit in hosts_data:
            db.add(models.Host(
                host_id=h_id,
                ip_address=ip,
                hostname=name,
                host_type=h_type,
                criticality=crit,
                first_seen=now - datetime.timedelta(days=7),
                last_seen=now
            ))
            
        # 2. Risk Scores
        risk_data = [
            ("10.0.0.1", 82.5, "HIGH", {"anomaly_type": "SMB_BURST", "confidence": 0.88}),
            ("10.0.0.2", 24.0, "NORMAL", {"anomaly_type": "BENIGN", "confidence": 0.95}),
            ("10.0.0.3", 15.0, "NORMAL", {"anomaly_type": "BENIGN", "confidence": 0.98}),
            ("10.0.0.4", 18.0, "NORMAL", {"anomaly_type": "BENIGN", "confidence": 0.97}),
            ("10.0.0.5", 88.0, "CRITICAL", {"anomaly_type": "PIVOT_ACTIVITY", "confidence": 0.91}),
            ("10.0.0.10", 94.5, "CRITICAL", {"anomaly_type": "DCSYNC_ATTEMPT", "confidence": 0.96}),
            ("10.0.0.11", 42.0, "NORMAL", {"anomaly_type": "HIGH_TRAFFIC", "confidence": 0.72}),
            ("10.0.0.20", 98.1, "CRITICAL", {"anomaly_type": "EXFIL_BURST", "confidence": 0.99}),
            ("10.0.0.30", 35.0, "NORMAL", {"anomaly_type": "GATEWAY_ROUTING", "confidence": 0.85})
        ]
        for host_ip, score, band, ev in risk_data:
            db.add(models.RiskScore(
                host_id=host_ip,
                score=score,
                severity_band=band,
                evidence=ev,
                timestamp=now
            ))

        # 3. Incidents
        incidents_data = [
            ("INC-2026-9041", "Lateral Movement & Domain Controller Compromise Attempt", "CRITICAL", "10.0.0.10", 94.5, "OPEN"),
            ("INC-2026-8812", "Unauthorized Credential Dumping on Internal Jump Box", "HIGH", "10.0.0.5", 88.0, "INVESTIGATING"),
            ("INC-2026-7643", "Anomalous Data Exfiltration Attempt against Production DB", "CRITICAL", "10.0.0.20", 98.1, "OPEN"),
            ("INC-2026-6520", "Suspicious Kerberos Ticket Request (Kerberoasting)", "HIGH", "10.0.0.1", 82.5, "RESOLVED"),
            ("INC-2026-5104", "Internal Subnet Reconnaissance & Stealth Port Scanning", "MEDIUM", "10.0.0.2", 45.0, "RESOLVED")
        ]
        
        for inc_id, title, sev, target, risk, stat in incidents_data:
            db.add(models.Incident(
                incident_id=inc_id,
                title=title,
                severity=sev,
                target_host=target,
                risk_score=risk,
                status=stat,
                created_at=now - datetime.timedelta(minutes=random.randint(15, 120)),
                updated_at=now - datetime.timedelta(minutes=random.randint(1, 10))
            ))

        # 4. Alerts
        alerts_data = [
            ("ALT-001", "INC-2026-9041", "10.0.0.10", "CRITICAL", {"technique": "T1003.006", "name": "DCSync Replication", "details": "Replication request from non-DC IP 10.0.0.5"}),
            ("ALT-002", "INC-2026-9041", "10.0.0.10", "CRITICAL", {"technique": "T1021.002", "name": "SMB Remote Services", "details": "PsExec execution over ADMIN$ share"}),
            ("ALT-003", "INC-2026-8812", "10.0.0.5", "HIGH", {"technique": "T1003.001", "name": "LSASS Memory Dump", "details": "Process memory access to lsass.exe detected"}),
            ("ALT-004", "INC-2026-8812", "10.0.0.5", "HIGH", {"technique": "T1021.004", "name": "SSH Brute Force Pivot", "details": "Anomalous internal SSH sessions from 10.0.0.1"}),
            ("ALT-005", "INC-2026-7643", "10.0.0.20", "CRITICAL", {"technique": "T1048", "name": "Exfiltration Over Protocol", "details": "High volume encrypted outbound payload from DB host"}),
            ("ALT-006", "INC-2026-6520", "10.0.0.1", "HIGH", {"technique": "T1059.001", "name": "PowerShell Scripting", "details": "Base64 encoded payload executed in user context"}),
            ("ALT-007", "INC-2026-5104", "10.0.0.2", "MEDIUM", {"technique": "T1046", "name": "Network Service Scanning", "details": "SYN sweep detected on ports 445, 3389, 22"})
        ]
        
        for alt_id, inc_id, host, sev, ev in alerts_data:
            db.add(models.Alert(
                alert_id=alt_id,
                incident_id=inc_id,
                host_id=host,
                severity=sev,
                evidence=ev,
                timestamp=now - datetime.timedelta(minutes=random.randint(5, 60))
            ))

        # 5. Graph Events (Topology and Attack Paths)
        # Normal + Lateral Movement Edges
        graph_edges = [
            # Attack Chain (High Risk Lateral Movement)
            ("10.0.0.1", "10.0.0.5", "SSH_SESSION", {"bytes": 45200, "packets": 320, "risk": 0.85}),
            ("10.0.0.5", "10.0.0.10", "SMB_ADMIN", {"bytes": 128400, "packets": 940, "risk": 0.94}),
            ("10.0.0.10", "10.0.0.20", "TDS_SQL", {"bytes": 840000, "packets": 4200, "risk": 0.98}),
            ("10.0.0.1", "10.0.0.2", "NETBIOS_SCAN", {"bytes": 1200, "packets": 15, "risk": 0.65}),
            ("10.0.0.1", "10.0.0.10", "KERBEROS_AS_REQ", {"bytes": 4500, "packets": 30, "risk": 0.75}),
            
            # Normal Enterprise Traffic
            ("10.0.0.2", "10.0.0.11", "SMTP_EMAIL", {"bytes": 18500, "packets": 80, "risk": 0.05}),
            ("10.0.0.3", "10.0.0.11", "IMAP_EMAIL", {"bytes": 32000, "packets": 120, "risk": 0.02}),
            ("10.0.0.4", "10.0.0.30", "HTTPS_GATEWAY", {"bytes": 95000, "packets": 510, "risk": 0.04}),
            ("10.0.0.2", "10.0.0.30", "HTTPS_GATEWAY", {"bytes": 62000, "packets": 340, "risk": 0.03}),
            ("10.0.0.3", "10.0.0.5", "SSH_DEV", {"bytes": 28000, "packets": 190, "risk": 0.12}),
            ("10.0.0.11", "10.0.0.30", "SMTP_RELAY", {"bytes": 142000, "packets": 800, "risk": 0.08}),
            ("10.0.0.10", "10.0.0.11", "LDAP_SYNC", {"bytes": 48000, "packets": 250, "risk": 0.05}),
            ("10.0.0.5", "10.0.0.30", "VPN_TUNNEL", {"bytes": 310000, "packets": 1600, "risk": 0.20}),
            ("10.0.0.20", "10.0.0.30", "BACKUP_SYNC", {"bytes": 920000, "packets": 4800, "risk": 0.35})
        ]
        
        for idx, (src, dst, etype, feat) in enumerate(graph_edges):
            db.add(models.GraphEvent(
                event_id=f"GE-{idx+1:03d}",
                node_a=src,
                node_b=dst,
                edge_type=etype,
                edge_features=feat,
                timestamp=now - datetime.timedelta(minutes=random.randint(1, 30))
            ))

        # 6. Containment Action
        db.add(models.ContainmentAction(
            host_id="10.0.0.1",
            action="ISOLATE",
            policy="DENY_ALL",
            reason="Automated containment triggered by Critical Risk score > 80",
            status="ACTIVE",
            timestamp=now - datetime.timedelta(minutes=45)
        ))

        # 7. Model Version
        db.add(models.ModelVersion(
            version_id="temporal_gnn_v1.2",
            trained_at=now - datetime.timedelta(days=2),
            dataset_ref="cicids2018_enterprise_graph",
            metrics={
                "Precision": 0.92,
                "Recall": 0.89,
                "F1": 0.905,
                "ROC-AUC": 0.965,
                "PR-AUC": 0.938
            },
            is_active=True
        ))
        
        db.commit()
        print("[Seed] Successfully seeded ThreatGraph database with rich demo data!")
        return {"status": "success", "message": "ThreatGraph seeded successfully"}
    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if close_at_end:
            db.close()

if __name__ == "__main__":
    seed_database()
