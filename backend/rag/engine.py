import re
from typing import List, Dict, Any

KNOWLEDGE_BASE = [
    {"id": "kb1", "content": "MITRE ATT&CK T1059: Command and Scripting Interpreter. Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries. These interfaces and languages provide ways of interacting with computer systems and are a common feature across many different platforms.", "tags": ["t1059", "execution"]},
    {"id": "kb2", "content": "MITRE ATT&CK T1021: Remote Services. Adversaries may use Valid Accounts to log into a service specifically designed to accept remote connections, such as telnet, SSH, and VNC. The adversary may then perform actions as the logged-on user.", "tags": ["t1021", "lateral_movement"]},
    {"id": "kb3", "content": "MITRE ATT&CK T1071: Application Layer Protocol. Adversaries may communicate using OSI application layer protocols to avoid detection/network filtering by blending in with existing traffic. Commands to the remote system, and often the results of those commands, will be embedded within the protocol traffic between the client and server.", "tags": ["t1071", "c2"]},
    {"id": "kb4", "content": "Runbook: High Risk Lateral Movement detected. Recommended action is immediate containment of the source host. Investigate the attack path and isolate critical assets downstream.", "tags": ["runbook", "containment", "lateral_movement"]}
]

class SimpleRAGEngine:
    """Mock RAG engine using basic keyword matching instead of pgvector/embeddings for local dev."""
    
    def __init__(self):
        self.kb = KNOWLEDGE_BASE
        
    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, str]]:
        query_words = set(re.findall(r'\w+', query.lower()))
        scored = []
        for doc in self.kb:
            score = 0
            doc_words = set(re.findall(r'\w+', doc["content"].lower()))
            for tag in doc["tags"]:
                doc_words.add(tag)
            
            # Simple Jaccard-like keyword overlap
            intersection = query_words.intersection(doc_words)
            if intersection:
                score = len(intersection)
            scored.append((score, doc))
            
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0]
