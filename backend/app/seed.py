import datetime
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models

def seed_database(db: Session = None, force: bool = False):
    close_at_end = False
    if db is None:
        db = SessionLocal()
        close_at_end = True
        
    try:
        # Create all tables if not exists
        models.Base.metadata.create_all(bind=engine)
        
        # Check if already seeded (unless force=True)
        existing_hosts = db.query(models.Host).count()
        if existing_hosts >= 25 and not force:
            print("[Seed] Database already contains large dataset. Skipping duplicate seed.")
            return {"status": "already_seeded", "hosts": existing_hosts}

        print("[Seed] Clearing old demo data and populating massive enterprise attack graph...")
        # Clear existing tables for a clean expansive graph
        db.query(models.AttackPath).delete()
        db.query(models.Alert).delete()
        db.query(models.Incident).delete()
        db.query(models.RiskScore).delete()
        db.query(models.GraphEvent).delete()
        db.query(models.ContainmentAction).delete()
        db.query(models.Host).delete()
        db.commit()

        now = datetime.datetime.utcnow()
        
        # 1. 35+ Enterprise Hosts across 5 Zones
        hosts_data = [
            # Zone 1: Perimeter & DMZ
            ("HOST-GW-01", "10.0.0.30", "perimeter-firewall-01", "GATEWAY", "HIGH"),
            ("HOST-RP-01", "10.0.0.31", "dmz-nginx-reverse-proxy", "SERVER", "HIGH"),
            ("HOST-VPN-01", "10.0.0.32", "corp-vpn-concentrator", "GATEWAY", "HIGH"),
            ("HOST-LB-01", "10.0.0.33", "cloud-edge-load-balancer", "GATEWAY", "MEDIUM"),

            # Zone 2: Identity & Core Infrastructure
            ("HOST-SRV-DC1", "10.0.0.10", "ad-primary-domain-controller", "DOMAIN_CONTROLLER", "CRITICAL"),
            ("HOST-SRV-DC2", "10.0.0.11", "ad-backup-domain-controller", "DOMAIN_CONTROLLER", "CRITICAL"),
            ("HOST-SRV-KDC", "10.0.0.12", "kerberos-kdc-server", "SERVER", "HIGH"),
            ("HOST-SRV-PKI", "10.0.0.13", "internal-ca-cert-authority", "SERVER", "HIGH"),
            ("HOST-SRV-MAIL", "10.0.0.14", "exchange-mail-cluster-01", "SERVER", "HIGH"),

            # Zone 3: Application Tier & Microservices
            ("HOST-SRV-JB01", "10.0.2.5", "jumpbox-admin-bastion", "SERVER", "HIGH"),
            ("HOST-K8S-M01", "10.0.2.6", "k8s-cluster-control-plane", "SERVER", "CRITICAL"),
            ("HOST-APP-AUTH", "10.0.2.7", "auth-oauth-microservice", "SERVER", "HIGH"),
            ("HOST-APP-PAY", "10.0.2.8", "payment-processing-engine", "SERVER", "CRITICAL"),
            ("HOST-APP-CACHE", "10.0.2.9", "redis-cluster-caching", "SERVER", "MEDIUM"),
            ("HOST-APP-API01", "10.0.2.15", "core-api-gateway-service", "SERVER", "HIGH"),
            ("HOST-APP-WORKER", "10.0.2.16", "async-task-worker-cluster", "SERVER", "MEDIUM"),

            # Zone 4: Crown Jewel Database Tier
            ("HOST-DB-PG01", "10.0.3.20", "prod-postgres-crown-jewel", "DATABASE", "CRITICAL"),
            ("HOST-DB-PG02", "10.0.3.21", "prod-postgres-replica-east", "DATABASE", "CRITICAL"),
            ("HOST-DB-MONGO", "10.0.3.22", "customer-document-mongodb", "DATABASE", "HIGH"),
            ("HOST-DB-BACKUP", "10.0.3.23", "encrypted-cold-storage-vault", "DATABASE", "CRITICAL"),
            ("HOST-DB-ANALYTICS", "10.0.3.24", "bi-data-warehouse-snowflake", "DATABASE", "HIGH"),

            # Zone 5: Corporate Endpoints (Workstations & Laptops)
            ("HOST-WS-SEC01", "10.0.1.10", "sec-research-workstation", "WORKSTATION", "MEDIUM"), # Patient zero
            ("HOST-WS-DEV01", "10.0.1.11", "senior-dev-workstation-01", "WORKSTATION", "LOW"),
            ("HOST-WS-DEV02", "10.0.1.12", "backend-dev-workstation-02", "WORKSTATION", "LOW"),
            ("HOST-WS-DEV03", "10.0.1.13", "frontend-dev-workstation-03", "WORKSTATION", "LOW"),
            ("HOST-WS-FIN01", "10.0.1.14", "finance-treasury-workstation", "WORKSTATION", "HIGH"),
            ("HOST-WS-FIN02", "10.0.1.15", "payroll-specialist-laptop", "LAPTOP", "MEDIUM"),
            ("HOST-WS-HR01", "10.0.1.16", "hr-recruiting-workstation", "WORKSTATION", "LOW"),
            ("HOST-WS-EXEC01", "10.0.1.17", "ciso-executive-macbook", "LAPTOP", "HIGH"),
            ("HOST-WS-EXEC02", "10.0.1.18", "cto-executive-laptop", "LAPTOP", "HIGH"),
            ("HOST-WS-QA01", "10.0.1.19", "qa-automation-runner", "WORKSTATION", "LOW"),
            ("HOST-WS-OPS01", "10.0.1.20", "sre-monitoring-console", "WORKSTATION", "MEDIUM"),
            ("HOST-WS-OPS02", "10.0.1.21", "network-admin-workstation", "WORKSTATION", "HIGH"),
            ("HOST-WS-CONT01", "10.0.1.22", "third-party-contractor-vdi", "WORKSTATION", "LOW"),
            ("HOST-WS-CORP01", "10.0.1.23", "legal-compliance-laptop", "LAPTOP", "MEDIUM"),
            ("HOST-WS-CORP02", "10.0.1.24", "marketing-analytics-workstation", "WORKSTATION", "LOW")
        ]
        
        for h_id, ip, name, h_type, crit in hosts_data:
            db.add(models.Host(
                host_id=h_id,
                ip_address=ip,
                hostname=name,
                host_type=h_type,
                criticality=crit,
                first_seen=now - datetime.timedelta(days=14),
                last_seen=now
            ))

        # 2. Risk Scores for key hosts
        risk_map = {
            "10.0.3.20": (98.5, "CRITICAL", {"reason": "Target of exfiltration burst & SQL injection staging", "confidence": 0.99}),
            "10.0.0.10": (95.0, "CRITICAL", {"reason": "Active Directory DCSync Replication attempt detected", "confidence": 0.97}),
            "10.0.2.5":  (91.2, "CRITICAL", {"reason": "Compromised jumpbox pivot host with abnormal SSH activity", "confidence": 0.94}),
            "10.0.1.10": (88.4, "HIGH",     {"reason": "Patient zero initial access via malicious payload", "confidence": 0.91}),
            "10.0.2.8":  (84.0, "HIGH",     {"reason": "Unauthorized API token extraction attempt", "confidence": 0.88}),
            "10.0.1.14": (76.5, "HIGH",     {"reason": "Suspicious NTLM relay authentication flood", "confidence": 0.82}),
            "10.0.1.12": (68.0, "MEDIUM",   {"reason": "Horizontal internal subnet port scanning", "confidence": 0.79}),
            "10.0.0.14": (44.0, "NORMAL",   {"reason": "High mail volume within expected threshold", "confidence": 0.65}),
            "10.0.0.30": (38.0, "NORMAL",   {"reason": "Edge traffic baseline routing", "confidence": 0.95}),
            "10.0.1.11": (12.0, "NORMAL",   {"reason": "Standard developer git / web traffic", "confidence": 0.99}),
            "10.0.1.17": (22.0, "NORMAL",   {"reason": "Encrypted VPN connection active", "confidence": 0.96}),
        }

        for ip, (score, band, ev) in risk_map.items():
            db.add(models.RiskScore(
                host_id=ip,
                score=score,
                severity_band=band,
                evidence=ev,
                timestamp=now
            ))

        # 3. Incidents
        incidents_data = [
            ("INC-2026-9041", "Advanced Lateral Movement & Active Directory DCSync Compromise", "CRITICAL", "10.0.0.10", 95.0, "OPEN"),
            ("INC-2026-8812", "Unauthorized Privilege Escalation & LSASS Dumping on Jumpbox", "CRITICAL", "10.0.2.5", 91.2, "INVESTIGATING"),
            ("INC-2026-7643", "Large-Scale Encrypted Data Exfiltration on Production Database", "CRITICAL", "10.0.3.20", 98.5, "OPEN"),
            ("INC-2026-6520", "Suspicious Kerberos Ticket Granting Service Abuse (Kerberoasting)", "HIGH", "10.0.0.12", 85.0, "INVESTIGATING"),
            ("INC-2026-5104", "Internal Subnet SYN Reconnaissance Sweep on Admin Ports", "MEDIUM", "10.0.1.12", 68.0, "RESOLVED"),
            ("INC-2026-4432", "Anomalous Payment Microservice JWT Token Hijacking", "HIGH", "10.0.2.8", 84.0, "OPEN"),
            ("INC-2026-3910", "Suspicious NTLM Relay Traffic from Finance Workstation", "MEDIUM", "10.0.1.14", 76.5, "INVESTIGATING"),
            ("INC-2026-2819", "Brute-force SSH Ingress Attempts against Bastion Host", "LOW", "10.0.0.32", 34.0, "RESOLVED")
        ]

        for inc_id, title, sev, target, risk, stat in incidents_data:
            db.add(models.Incident(
                incident_id=inc_id,
                title=title,
                severity=sev,
                target_host=target,
                risk_score=risk,
                status=stat,
                created_at=now - datetime.timedelta(minutes=random.randint(20, 240)),
                updated_at=now - datetime.timedelta(minutes=random.randint(1, 15))
            ))

        # 4. Alerts
        alerts_data = [
            ("ALT-001", "INC-2026-9041", "10.0.0.10", "CRITICAL", {"technique": "T1003.006", "name": "DCSync Replication", "details": "Directory replication triggered from non-DC IP 10.0.2.5"}),
            ("ALT-002", "INC-2026-9041", "10.0.0.10", "CRITICAL", {"technique": "T1021.002", "name": "SMB Remote Services", "details": "PsExec execution over ADMIN$ share"}),
            ("ALT-003", "INC-2026-8812", "10.0.2.5",  "CRITICAL", {"technique": "T1003.001", "name": "LSASS Memory Dump", "details": "MiniDumpWriteDump API invoked against lsass.exe process"}),
            ("ALT-004", "INC-2026-8812", "10.0.2.5",  "HIGH",     {"technique": "T1021.004", "name": "SSH Brute-Force Pivot", "details": "Abnormal SSH tunneling from 10.0.1.10"}),
            ("ALT-005", "INC-2026-7643", "10.0.3.20", "CRITICAL", {"technique": "T1048", "name": "Exfiltration Over Protocol", "details": "High volume encrypted payload transferred to edge proxy"}),
            ("ALT-006", "INC-2026-6520", "10.0.0.12", "HIGH",     {"technique": "T1558.003", "name": "Kerberoasting Request", "details": "RC4-HMAC ticket requests for multiple service accounts"}),
            ("ALT-007", "INC-2026-5104", "10.0.1.12", "MEDIUM",   {"technique": "T1046", "name": "Network Service Scanning", "details": "Rapid SYN scan detected across ports 445, 3389, 22, 5432"}),
            ("ALT-008", "INC-2026-4432", "10.0.2.8",  "HIGH",     {"technique": "T1528", "name": "Steal Application Access Token", "details": "Admin JWT token reused from untrusted IP 10.0.1.14"}),
            ("ALT-009", "INC-2026-3910", "10.0.1.14", "MEDIUM",   {"technique": "T1557.001", "name": "LLMNR/NBT-NS Poisoning", "details": "Inbound NTLMv2 challenge-response captures"}),
            ("ALT-010", "INC-2026-9041", "10.0.1.10", "HIGH",     {"technique": "T1059.001", "name": "PowerShell Encoded Script", "details": "Base64 encoded payload executed in user context"})
        ]

        for alt_id, inc_id, host, sev, ev in alerts_data:
            db.add(models.Alert(
                alert_id=alt_id,
                incident_id=inc_id,
                host_id=host,
                severity=sev,
                evidence=ev,
                timestamp=now - datetime.timedelta(minutes=random.randint(5, 120))
            ))

        # 5. 75+ Graph Events (Massive Enterprise Interconnected Network Map)
        graph_edges = [
            # === Multi-Hop Lateral Movement Attack Vector 1 (Red Critical Path) ===
            ("10.0.1.10", "10.0.2.5", "SSH_TUNNEL", {"bytes": 84500, "packets": 720, "risk": 0.88, "attack_vector": "PIVOT"}),
            ("10.0.2.5", "10.0.0.10", "SMB_PSEXEC", {"bytes": 248000, "packets": 1850, "risk": 0.95, "attack_vector": "LATERAL_MOVEMENT"}),
            ("10.0.0.10", "10.0.3.20", "SQL_ADMIN_LINK", {"bytes": 1420000, "packets": 8900, "risk": 0.98, "attack_vector": "EXFILTRATION_STAGE"}),
            ("10.0.3.20", "10.0.0.31", "HTTPS_EXFIL_PROXY", {"bytes": 4850000, "packets": 24000, "risk": 0.99, "attack_vector": "DATA_EXFIL"}),
            ("10.0.0.31", "10.0.0.30", "EGRESS_TUNNEL", {"bytes": 4900000, "packets": 24200, "risk": 0.97, "attack_vector": "EXTERNAL_C2"}),

            # === Secondary Attack Vector 2 (Kerberoasting & Finance Infiltration) ===
            ("10.0.1.14", "10.0.0.12", "KERB_TGS_REQ", {"bytes": 14500, "packets": 95, "risk": 0.85, "attack_vector": "KERBEROAST"}),
            ("10.0.1.14", "10.0.2.8", "REST_ADMIN_API", {"bytes": 62000, "packets": 410, "risk": 0.84, "attack_vector": "TOKEN_ABUSE"}),
            ("10.0.2.8", "10.0.3.21", "DB_REPLICA_QUERY", {"bytes": 310000, "packets": 1700, "risk": 0.78, "attack_vector": "UNAUTHORIZED_READ"}),

            # === Reconnaissance Scan Vector 3 ===
            ("10.0.1.12", "10.0.2.5", "TCP_SYN_SCAN", {"bytes": 1800, "packets": 24, "risk": 0.68, "attack_vector": "PORT_SCAN"}),
            ("10.0.1.12", "10.0.2.6", "TCP_SYN_SCAN", {"bytes": 1800, "packets": 24, "risk": 0.68, "attack_vector": "PORT_SCAN"}),
            ("10.0.1.12", "10.0.2.7", "TCP_SYN_SCAN", {"bytes": 1800, "packets": 24, "risk": 0.68, "attack_vector": "PORT_SCAN"}),
            ("10.0.1.12", "10.0.2.9", "TCP_SYN_SCAN", {"bytes": 1800, "packets": 24, "risk": 0.68, "attack_vector": "PORT_SCAN"}),
            ("10.0.1.10", "10.0.1.11", "NETBIOS_SCAN", {"bytes": 2400, "packets": 32, "risk": 0.62, "attack_vector": "INTERNAL_RECON"}),
            ("10.0.1.10", "10.0.1.13", "NETBIOS_SCAN", {"bytes": 2400, "packets": 32, "risk": 0.62, "attack_vector": "INTERNAL_RECON"}),

            # === Normal Enterprise Business Flows (Identity & PKI) ===
            ("10.0.0.10", "10.0.0.11", "AD_REPLICATION", {"bytes": 320000, "packets": 1900, "risk": 0.02}),
            ("10.0.0.10", "10.0.0.12", "KDC_SYNC", {"bytes": 84000, "packets": 520, "risk": 0.01}),
            ("10.0.0.10", "10.0.0.13", "CA_CERT_SYNC", {"bytes": 42000, "packets": 280, "risk": 0.01}),
            ("10.0.0.10", "10.0.0.14", "LDAP_GLOBAL_CATALOG", {"bytes": 115000, "packets": 780, "risk": 0.03}),

            # === Application Microservices Mesh ===
            ("10.0.0.31", "10.0.2.15", "HTTP_ROUTING", {"bytes": 950000, "packets": 5400, "risk": 0.05}),
            ("10.0.2.15", "10.0.2.7", "RPC_AUTH_VERIFY", {"bytes": 180000, "packets": 1100, "risk": 0.02}),
            ("10.0.2.15", "10.0.2.8", "RPC_PAYMENT", {"bytes": 240000, "packets": 1400, "risk": 0.04}),
            ("10.0.2.15", "10.0.2.9", "REDIS_GET", {"bytes": 450000, "packets": 3100, "risk": 0.01}),
            ("10.0.2.6", "10.0.2.15", "K8S_HEALTH_PROBE", {"bytes": 32000, "packets": 210, "risk": 0.01}),
            ("10.0.2.6", "10.0.2.16", "K8S_POD_DISPATCH", {"bytes": 540000, "packets": 3200, "risk": 0.02}),
            ("10.0.2.16", "10.0.2.9", "REDIS_QUEUE", {"bytes": 280000, "packets": 1800, "risk": 0.01}),
            ("10.0.2.8", "10.0.3.20", "SQL_TRANSACTION", {"bytes": 890000, "packets": 4800, "risk": 0.03}),
            ("10.0.2.7", "10.0.3.20", "SQL_USER_AUTH", {"bytes": 420000, "packets": 2600, "risk": 0.02}),
            ("10.0.2.16", "10.0.3.22", "MONGO_LOG_WRITE", {"bytes": 620000, "packets": 3800, "risk": 0.02}),

            # === Database Cluster & Replication ===
            ("10.0.3.20", "10.0.3.21", "WAL_REPLICATION", {"bytes": 2400000, "packets": 12000, "risk": 0.02}),
            ("10.0.3.20", "10.0.3.23", "ENCRYPTED_SNAPSHOT", {"bytes": 5600000, "packets": 28000, "risk": 0.05}),
            ("10.0.3.21", "10.0.3.24", "ETL_PIPELINE", {"bytes": 3100000, "packets": 16000, "risk": 0.03}),

            # === Workstation Corporate Traffic ===
            ("10.0.1.11", "10.0.0.14", "SMTP_EMAIL", {"bytes": 28000, "packets": 160, "risk": 0.02}),
            ("10.0.1.12", "10.0.0.14", "IMAP_EMAIL", {"bytes": 34000, "packets": 190, "risk": 0.01}),
            ("10.0.1.13", "10.0.0.30", "HTTPS_INTERNET", {"bytes": 420000, "packets": 2200, "risk": 0.03}),
            ("10.0.1.14", "10.0.0.10", "KERB_AUTH", {"bytes": 18000, "packets": 120, "risk": 0.02}),
            ("10.0.1.15", "10.0.0.14", "OUTLOOK_WEB", {"bytes": 45000, "packets": 280, "risk": 0.02}),
            ("10.0.1.16", "10.0.0.30", "HTTPS_INTERNET", {"bytes": 180000, "packets": 980, "risk": 0.02}),
            ("10.0.1.17", "10.0.0.32", "IPSEC_VPN", {"bytes": 840000, "packets": 4200, "risk": 0.04}),
            ("10.0.1.18", "10.0.0.32", "IPSEC_VPN", {"bytes": 920000, "packets": 4600, "risk": 0.04}),
            ("10.0.1.19", "10.0.2.15", "QA_API_TEST", {"bytes": 380000, "packets": 2100, "risk": 0.03}),
            ("10.0.1.20", "10.0.2.6", "K8S_METRICS", {"bytes": 210000, "packets": 1300, "risk": 0.02}),
            ("10.0.1.21", "10.0.0.30", "SSH_FIREWALL_ADMIN", {"bytes": 95000, "packets": 580, "risk": 0.08}),
            ("10.0.1.22", "10.0.0.31", "VDI_WEB_SESSION", {"bytes": 620000, "packets": 3400, "risk": 0.05}),
            ("10.0.1.23", "10.0.0.10", "LDAP_LOOKUP", {"bytes": 22000, "packets": 140, "risk": 0.01}),
            ("10.0.1.24", "10.0.3.24", "SNOWFLAKE_QUERY", {"bytes": 740000, "packets": 3900, "risk": 0.04}),

            # === Cross-Subnet Core Connectivity ===
            ("10.0.0.30", "10.0.0.31", "DMZ_ROUTING", {"bytes": 8200000, "packets": 42000, "risk": 0.02}),
            ("10.0.0.30", "10.0.0.32", "VPN_INTERFACE", {"bytes": 2400000, "packets": 13000, "risk": 0.03}),
            ("10.0.0.30", "10.0.0.33", "BGP_EDGE_ROUTING", {"bytes": 6500000, "packets": 34000, "risk": 0.01}),
            ("10.0.0.32", "10.0.2.5", "BASTION_SESSION", {"bytes": 140000, "packets": 890, "risk": 0.15}),
            ("10.0.2.5", "10.0.2.6", "ADMIN_KUBECTL", {"bytes": 88000, "packets": 540, "risk": 0.12}),
            ("10.0.0.14", "10.0.0.30", "SMTP_OUTBOUND_MX", {"bytes": 580000, "packets": 3200, "risk": 0.04})
        ]

        for idx, (src, dst, etype, feat) in enumerate(graph_edges):
            db.add(models.GraphEvent(
                event_id=f"GE-{idx+1:04d}",
                node_a=src,
                node_b=dst,
                edge_type=etype,
                edge_features=feat,
                timestamp=now - datetime.timedelta(minutes=random.randint(1, 45))
            ))

        # 6. Containment Actions
        db.add(models.ContainmentAction(
            host_id="10.0.1.10",
            action="ISOLATE",
            policy="DENY_ALL",
            reason="Automated quarantine: Patient Zero Lateral Movement Pivot",
            status="ACTIVE",
            timestamp=now - datetime.timedelta(minutes=60)
        ))
        db.add(models.ContainmentAction(
            host_id="10.0.2.5",
            action="ISOLATE",
            policy="DENY_ALL",
            reason="Analyst containment: Compromised Jumpbox Host",
            status="ACTIVE",
            timestamp=now - datetime.timedelta(minutes=25)
        ))

        # 7. Model Version
        db.add(models.ModelVersion(
            version_id="temporal_gnn_v2.0",
            trained_at=now - datetime.timedelta(days=1),
            dataset_ref="cicids2018_enterprise_graph_expanded",
            metrics={
                "Precision": 0.935,
                "Recall": 0.912,
                "F1": 0.923,
                "ROC-AUC": 0.978,
                "PR-AUC": 0.949
            },
            is_active=True
        ))
        
        db.commit()
        print(f"[Seed] Successfully seeded ThreatGraph with {len(hosts_data)} hosts and {len(graph_edges)} graph events!")
        return {
            "status": "success", 
            "hosts_count": len(hosts_data), 
            "graph_events_count": len(graph_edges),
            "incidents_count": len(incidents_data),
            "alerts_count": len(alerts_data)
        }
    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding database: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if close_at_end:
            db.close()

if __name__ == "__main__":
    seed_database(force=True)
