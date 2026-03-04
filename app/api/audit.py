from fastapi import APIRouter
from app.core.db import SessionLocal
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditResponse

router = APIRouter()


@router.get("/", response_model=list[AuditResponse])
def get_audit_logs():
    db = SessionLocal()
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    db.close()
    return logs