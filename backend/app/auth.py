from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

SECRET_KEY = "threatgraph-secret-key-mock"
ALGORITHM = "HS256"

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

def require_analyst(payload: dict = Depends(verify_token)):
    role = payload.get("role")
    if role not in ["ANALYST", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return payload

def log_audit(db, user_id: str, role: str, action: str, resource: str, status_str: str):
    from app.models import AuditLog
    audit = AuditLog(
        user_id=user_id,
        role=role,
        action=action,
        resource=resource,
        status=status_str
    )
    db.add(audit)
    db.commit()
