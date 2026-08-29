# NetRaptor-X API Contract (OpenAPI Stub)

```yaml
openapi: 3.0.3
info:
  title: NetRaptor-X API
  version: 1.0.0
paths:
  /health:
    get:
      summary: Service health check
      responses:
        '200':
          description: OK
  /metrics:
    get:
      summary: Prometheus metrics
      responses:
        '200':
          description: OK
  /hosts:
    get:
      summary: List monitored hosts
      responses:
        '501':
          description: Not Implemented
  /hosts/{id}/risk:
    get:
      summary: Get host risk score
      responses:
        '501':
          description: Not Implemented
  /network/graph:
    get:
      summary: Get current network graph
      responses:
        '501':
          description: Not Implemented
  /network/topology:
    get:
      summary: Get network topology
      responses:
        '501':
          description: Not Implemented
  /threats:
    get:
      summary: List active threats
      responses:
        '501':
          description: Not Implemented
  /incidents:
    get:
      summary: List incidents
      responses:
        '501':
          description: Not Implemented
  /incidents/{id}:
    get:
      summary: Get incident details
      responses:
        '501':
          description: Not Implemented
  /incidents/{id}/attack-path:
    get:
      summary: Get attack path for incident
      responses:
        '501':
          description: Not Implemented
  /alerts:
    get:
      summary: List alerts
      responses:
        '501':
          description: Not Implemented
  /models:
    get:
      summary: List model versions
      responses:
        '501':
          description: Not Implemented
  /models/{id}/metrics:
    get:
      summary: Get metrics for a model
      responses:
        '501':
          description: Not Implemented
  /models/{id}/predictions:
    get:
      summary: Get predictions from a model
      responses:
        '501':
          description: Not Implemented
  /containment/isolate/{host_id}:
    post:
      summary: Isolate a host
      responses:
        '501':
          description: Not Implemented
  /containment/release/{host_id}:
    post:
      summary: Release an isolated host
      responses:
        '501':
          description: Not Implemented
  /policies:
    get:
      summary: List network policies
      responses:
        '501':
          description: Not Implemented
    post:
      summary: Create network policy
      responses:
        '501':
          description: Not Implemented
  /policies/{id}:
    delete:
      summary: Delete network policy
      responses:
        '501':
          description: Not Implemented
  /soc/investigate/{incident_id}:
    post:
      summary: Generate LLM investigation report
      responses:
        '501':
          description: Not Implemented
  /soc/query:
    post:
      summary: Query LLM about incidents
      responses:
        '501':
          description: Not Implemented
  /simulation:
    post:
      summary: Control synthetic traffic generation
      responses:
        '501':
          description: Not Implemented
```
