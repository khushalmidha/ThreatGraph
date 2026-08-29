import json
import datetime
from typing import Dict, Any, List

class SOCAnalystLLM:
    def __init__(self):
        # We mock the LLM calls so we don't require external API keys to run.
        pass
        
    def investigate(self, incident: Dict[str, Any], attack_path: Dict[str, Any], context: List[Dict[str, Any]]) -> str:
        """
        Simulates an LLM structured investigation report grounded in retrieved evidence.
        The LLM is prompted to explicitly label every claim.
        """
        # Build the prompt
        evidence_str = "\n".join([f"- {c['content']}" for c in context])
        
        # We simulate the LLM's response generation directly.
        # In a real system we'd pass `evidence_str` to an LLM with strict JSON schema forcing.
        
        # Check if we have context to prevent hallucination
        if not context:
            return """# Incident Investigation Report

**Observed Evidence:** None.
**Uncertainty:** HIGH. Cannot provide a confident investigation without retrieved context or evidence.
"""
            
        mitre_mapping = "T1021: Remote Services" if "t1021" in str(context).lower() else "Unknown"
        
        report = f"""# Incident Investigation Report

**Incident Summary**
[Observed] High risk activity detected on host {incident.get('target_host')} at {incident.get('updated_at')}.

**Severity**
[Observed] {incident.get('severity')}

**Primary Host**
[Observed] {incident.get('target_host')}

**Likely Behavior**
[Inferred] The observed traffic patterns and risk scores suggest lateral movement and unauthorized remote access.

**Confidence**
[Inferred] High, based on the fusion model score of {incident.get('risk_score', 'N/A')}.

**Observed Evidence**
[Observed] 
{evidence_str}

**Potential ATT&CK Mapping**
[Inferred] {mitre_mapping}

**Affected Assets**
[Observed] Blast radius includes: {', '.join(attack_path.get('blast_radius', []))}

**Attack Path**
[Observed] Most likely propagation path: {' -> '.join(attack_path.get('likely_path', []))}

**Recommended Actions**
[Recommended] Immediate network isolation of {incident.get('target_host')}. Revoke active session tokens.

**Containment Recommendation**
[Recommended] Isolate {incident.get('target_host')} and {', '.join(attack_path.get('critical_assets', []))}.

**Uncertainty**
[Inferred] LOW. Supported by multiple high-confidence telemetry signals and runbooks.
"""
        return report

    def query(self, user_query: str, context: List[Dict[str, Any]]) -> str:
        """
        Simulates answering a user query using only retrieved context.
        """
        if not context:
            return "I don't have enough retrieved evidence to answer that confidently."
            
        evidence_str = "\n".join([f"- {c['content']}" for c in context])
        return f"Based on the observed evidence:\n\n{evidence_str}\n\n[Inferred] The query relates to the above techniques/runbooks."
