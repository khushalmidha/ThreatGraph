# NetRaptor-X Architecture

## System Design
NetRaptor-X is built on a modular, event-driven architecture simulating a modern Security Operations Center (SOC). It spans from network telemetry generation to automated threat mitigation, leveraging machine learning and generative AI at critical decision points.

## Comprehensive Architecture Diagram

```mermaid
graph TD
    %% Styling
    classDef generator fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef messageBus fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#fff
    classDef processing fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#fff
    classDef mlEngine fill:#1e293b,stroke:#8b5cf6,stroke-width:2px,color:#fff
    classDef datastore fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#fff
    classDef frontend fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#fff
    
    subgraph "1. Data Generation & Ingestion"
        TG[Traffic Generator <br> Python / Synthetic]:::generator
        ZTA[Zero-Trust Zones <br> Web/App/DB]:::generator
        Kafka[(Kafka Event Stream <br> Raw Flows & Logs)]:::messageBus
        
        TG -->|Simulated Network Traffic| ZTA
        ZTA -->|Telemetry| Kafka
    end

    subgraph "2. Stream Processing & State"
        GraphWorker[Graph Worker <br> Real-time Edge Updates]:::processing
        FeatExtractor[Feature Extractor <br> Temporal Windows]:::processing
        NX[(In-Memory Graph <br> NetworkX)]:::datastore
        
        Kafka --> GraphWorker
        Kafka --> FeatExtractor
        GraphWorker --> NX
        FeatExtractor --> NX
    end

    subgraph "3. AI Threat Detection Engine"
        GNN[Graph Neural Network <br> Spatial Context]:::mlEngine
        Transformer[Time-Series Transformer <br> Temporal Behavior]:::mlEngine
        Fusion[Fusion Layer <br> MLP Classifier]:::mlEngine
        
        NX -->|Node Neighborhoods| GNN
        NX -->|Historical Features| Transformer
        GNN --> Fusion
        Transformer --> Fusion
        Fusion -->|Risk Score 0.0 - 1.0| RiskEngine[Risk Evaluation Engine]:::processing
    end

    subgraph "4. Automated Response & SOC"
        IncidentDB[(Incident Database <br> SQLite/JSON)]:::datastore
        AttackGraph[Attack Path Engine <br> Dijkstra/BFS]:::processing
        LLM[RAG SOC Analyst <br> GPT/Local LLM]:::mlEngine
        FAISS[(FAISS Vector Store <br> MITRE ATT&CK)]:::datastore
        Containment[Software Firewall <br> Policy Enforcement]:::processing
        
        RiskEngine -->|Score > 80| IncidentDB
        RiskEngine -->|Trigger| AttackGraph
        NX --> AttackGraph
        AttackGraph -->|Blast Radius| LLM
        FAISS -->|Context Retrieval| LLM
        IncidentDB --> Containment
        Containment -.->|Quarantine / Drop Traffic| ZTA
    end

    subgraph "5. Presentation Layer"
        FastAPI[FastAPI Backend <br> REST & SSE]:::processing
        ReactUI[React + Vite Dashboard <br> TailwindCSS]:::frontend
        
        IncidentDB --> FastAPI
        LLM --> FastAPI
        Containment --> FastAPI
        FastAPI -->|Live Updates| ReactUI
    end
```

## Component Breakdown

1. **Traffic Generation**: Synthetically generates NetFlow-like telemetry within a micro-segmented network. Injects anomalous lateral movement paths based on probability thresholds.
2. **Stream Processing**: Consumes events and maintains a real-time directed graph of network communications, calculating sliding-window features (degrees, PageRank, bytes).
3. **AI Engine**: A hybrid PyTorch model. The GNN embeds structural topology (who talks to whom), and the Transformer embeds behavioral shifts (how traffic volume changes).
4. **SOC & Containment**: Detects high-risk nodes, reconstructs the attack path to patient-zero, queries a local RAG Knowledge Base to explain the MITRE technique, and triggers a firewall isolation policy.
5. **Dashboard**: Live React interface tracking real-time risk scores, active incidents, and visual topology of the compromised zones.
